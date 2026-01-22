
# Boot-Time Compliance Gate (MetaBlooms OS v2.0)

At OS boot:
1. Load /spec/METABLOOMS_MANIFEST.json
2. Verify SHA256 hashes of all spec files
3. Fail boot if any file is missing or mismatched
4. Expose runtime flags:
   - METABLOOMS_ACTIVE = true/false
   - METABLOOMS_KERNEL_VERSION = v2.0
5. Abort task execution unless METABLOOMS_ACTIVE == true
