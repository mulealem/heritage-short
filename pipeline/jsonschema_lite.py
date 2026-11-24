"""Tiny JSON Schema (draft-07 subset) validator — stdlib only.

Supports the keywords used by schema/storyboard.schema.json:
type, required, properties, additionalProperties, items, enum, const,
minimum/maximum, minLength/maxLength, minItems/maxItems, pattern.
Good enough for our contract; not a general-purpose validator.
"""
import re

def validate(obj, schema, path="$"):
    errors = []
    _v(obj, schema, path, errors)
    return errors


def _v(obj, sch, path, errors):
    if not isinstance(sch, dict):
        return
    t = sch.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_type_ok(obj, tt) for tt in types):
            errors.append("%s: expected type %s, got %s" % (path, t, type(obj).__name__))
            return
    if "const" in sch and obj != sch["const"]:
        errors.append("%s: expected const %r, got %r" % (path, sch["const"], obj))
    if "enum" in sch and obj not in sch["enum"]:
        errors.append("%s: must be one of %s, got %r" % (path, sch["enum"], obj))
    if isinstance(obj, str):
        if "minLength" in sch and len(obj) < sch["minLength"]:
            errors.append("%s: shorter than minLength=%d" % (path, sch["minLength"]))
        if "maxLength" in sch and len(obj) > sch["maxLength"]:
            errors.append("%s: longer than maxLength=%d" % (path, sch["maxLength"]))
        if "pattern" in sch and not re.search(sch["pattern"], obj):
            errors.append("%s: does not match pattern %r (%r)" % (path, sch["pattern"], obj))
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if "minimum" in sch and obj < sch["minimum"]:
            errors.append("%s: below minimum %s" % (path, sch["minimum"]))
        if "maximum" in sch and obj > sch["maximum"]:
            errors.append("%s: above maximum %s" % (path, sch["maximum"]))
    if isinstance(obj, dict):
        for r in sch.get("required", []):
            if r not in obj:
                errors.append("%s: missing required property %r" % (path, r))
        props = sch.get("properties", {})
        if sch.get("additionalProperties") is False:
            for k in obj:
                if k not in props:
                    errors.append("%s: unexpected property %r" % (path, k))
        for k, v in obj.items():
            if k in props:
                _v(v, props[k], "%s.%s" % (path, k), errors)
    if isinstance(obj, list):
        if "minItems" in sch and len(obj) < sch["minItems"]:
            errors.append("%s: fewer than minItems=%d" % (path, sch["minItems"]))
        if "maxItems" in sch and len(obj) > sch["maxItems"]:
            errors.append("%s: more than maxItems=%d" % (path, sch["maxItems"]))
        if "items" in sch:
            for i, item in enumerate(obj):
                _v(item, sch["items"], "%s[%d]" % (path, i), errors)


def _type_ok(obj, t):
    return {
        "object": isinstance(obj, dict),
        "array": isinstance(obj, list),
        "string": isinstance(obj, str),
        "integer": isinstance(obj, int) and not isinstance(obj, bool),
        "number": isinstance(obj, (int, float)) and not isinstance(obj, bool),
        "boolean": isinstance(obj, bool),
        "null": obj is None,
    }.get(t, True)
