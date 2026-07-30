import { describe, expect, it } from "vitest";
import Ajv2020 from "ajv/dist/2020";
import schema from "../../schemas/protocol_message.schema.json";

describe("MetaBlooms IRE protocol schema", () => {
  it("rejects messages over the published version", () => {
    const validate = new Ajv2020({ allErrors: true, strict: true }).compile(schema);
    expect(validate({
      schema: "mb.ire.protocol.v99",
      type: "HELLO",
      message_id: "msg-1",
      payload: {},
    })).toBe(false);
  });

  it("accepts a version-one hello message", () => {
    const validate = new Ajv2020({ allErrors: true, strict: true }).compile(schema);
    expect(validate({
      schema: "mb.ire.protocol.v1",
      type: "HELLO",
      message_id: "msg-1",
      payload: {},
    })).toBe(true);
  });
});
