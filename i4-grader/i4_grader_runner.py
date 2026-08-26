#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.metadata as md, json, os, platform, re, subprocess, sys, time
from pathlib import Path
from typing import Any

from huggingface_hub import model_info
from inspect_ai import Task, eval
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import GenerateConfig, get_model
from inspect_ai.scorer import model_graded_fact
from inspect_ai.solver import solver

GRADE_RE = re.compile(r"(?im)GRADE\s*:\s*([CI])")


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)+'\n', encoding='utf-8')


@solver
def fixed_candidate_answer():
    async def solve(state, generate):
        state.output.completion=str(state.metadata['candidate_answer'])
        return state
    return solve


def score_rows(log, corpus):
    by_id={c['case_id']:c for c in corpus['cases']}
    rows=[]
    for sample in log.samples or []:
        cid=str(sample.id)
        score=None
        if sample.scores:
            score=next(iter(sample.scores.values()))
        value=None if score is None else score.value
        grade=value if isinstance(value,str) and value in ('C','I') else None
        explanation='' if score is None or score.explanation is None else str(score.explanation)
        rows.append({
            'case_id':cid,
            'grade':grade,
            'gold':by_id[cid]['gold'],
            'critical':bool(by_id[cid]['critical']),
            'parse_failure':grade is None,
            'explanation':explanation,
            'answer':'' if score is None or score.answer is None else str(score.answer),
        })
    rows.sort(key=lambda x:x['case_id'])
    return rows


def one_run(corpus, model_id: str, revision: str, mode: str, seed: int | None, log_dir: Path):
    samples=[Sample(input=c['question'], target=c['reference'], id=c['case_id'], metadata={'candidate_answer':c['candidate_answer']}) for c in corpus['cases']]
    if mode=='deterministic':
        cfg=GenerateConfig(max_tokens=12, seed=0, temperature=None, top_p=None)
        do_sample=False
    else:
        cfg=GenerateConfig(max_tokens=12, seed=seed, temperature=0.7, top_p=0.9)
        do_sample=True
    grader=get_model('hf/'+model_id, config=cfg, memoize=False, device='cpu', do_sample=do_sample, revision=revision)
    scorer=model_graded_fact(
        model=grader,
        partial_credit=False,
        instructions='Return exactly one line: GRADE: C if the submission contains the factual content in the expert answer; otherwise return exactly one line: GRADE: I. Do not include reasoning or any other text.',
        grade_pattern=r'(?im)^\s*GRADE\s*:\s*([CI])\s*$'
    )
    task=Task(dataset=MemoryDataset(samples, name='metablooms-i4-semantic-grading'), solver=fixed_candidate_answer(), scorer=scorer, name='metablooms_i4_model_grader')
    started=time.perf_counter()
    logs=eval(task, model='mockllm/model', log_dir=str(log_dir), display='none', trace=True, log_samples=True)
    elapsed=time.perf_counter()-started
    if len(logs)!=1:
        raise RuntimeError(f'expected one Inspect log, got {len(logs)}')
    log=logs[0]
    rows=score_rows(log, corpus)
    return {
        'mode':mode,'seed':seed,'elapsed_seconds':elapsed,'status':log.status,
        'inspect_log_path':str(log.location),'cases':rows,
        'valid_grade_count':sum(1 for r in rows if r['grade'] in ('C','I')),
        'parse_failure_count':sum(1 for r in rows if r['grade'] is None),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True)
    ap.add_argument('--model-id', required=True)
    ap.add_argument('--model-slug', required=True)
    ap.add_argument('--out-dir', required=True)
    args=ap.parse_args()
    corpus_path=Path(args.corpus).resolve(); out=Path(args.out_dir).resolve(); out.mkdir(parents=True, exist_ok=True)
    corpus=json.loads(corpus_path.read_text(encoding='utf-8'))
    info=model_info(args.model_id)
    revision=info.sha
    if not revision:
        raise RuntimeError('model revision unavailable')
    inspect_version=md.version('inspect-ai')
    if inspect_version!='0.3.260':
        raise RuntimeError(f'wrong Inspect version {inspect_version}')
    freeze=subprocess.run([sys.executable,'-m','pip','freeze','--all'],check=True,capture_output=True,text=True).stdout
    (out/'PIP_FREEZE.txt').write_text(freeze,encoding='utf-8')
    runs=[]
    runs.append(one_run(corpus,args.model_id,revision,'deterministic',0,out/'logs_deterministic'))
    for seed in (11,22,33):
        runs.append(one_run(corpus,args.model_id,revision,'stochastic',seed,out/f'logs_seed_{seed}'))
    payload={
        'schema':'mb.inspect_i4_remote_grader_result.v1',
        'grader_family':args.model_slug,
        'model_id':args.model_id,
        'model_revision':revision,
        'inspect_version':inspect_version,
        'corpus_sha256':sha256_file(corpus_path),
        'python_version':platform.python_version(),
        'platform':platform.platform(),
        'machine':platform.machine(),
        'package_freeze_sha256':hashlib.sha256(freeze.encode()).hexdigest(),
        'grader_protocol':os.environ.get('I4_GRADER_PROTOCOL','concise-grade-v2'),
        'runs':runs,
        'promotion_authorized':False,
    }
    write_json(out/'GRADER_RESULT.json',payload)
    manifest=[]
    for p in sorted(x for x in out.rglob('*') if x.is_file()):
        manifest.append({'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':sha256_file(p)})
    write_json(out/'ARTIFACT_MANIFEST.json',{'schema':'mb.inspect_i4_remote_artifact_manifest.v1','files':manifest})
    print('I4_REMOTE_GRADER_RESULT='+str(out/'GRADER_RESULT.json'))
    print('I4_MODEL_ID='+args.model_id)
    print('I4_MODEL_REVISION='+revision)
    print('I4_INSPECT_VERSION='+inspect_version)
    print('I4_CORPUS_SHA256='+sha256_file(corpus_path))

if __name__=='__main__':
    main()
