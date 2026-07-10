-- Reversible byte transform over a bytea column, expressed as a PL/pgSQL
-- stored procedure. Calling it twice with the same argument restores the
-- original value, since the position/argument-derived mixin does not depend
-- on the payload.

CREATE OR REPLACE FUNCTION transform_bytes(payload bytea, param bytea)
RETURNS bytea AS $$
DECLARE
    result bytea := '\x'::bytea;
    n integer := octet_length(payload);
    m integer := octet_length(param);
    b integer;
    k integer;
    acc integer := m;
    mixin integer;
BEGIN
    FOR i IN 0 .. n - 1 LOOP
        b := get_byte(payload, i);
        k := get_byte(param, i % m);
        acc := (acc * 31 + k + i) % 256;
        mixin := ((acc << 3) | (acc >> 5)) & 255;
        mixin := (mixin # k) & 255;
        result := result || set_byte('\x00'::bytea, 0, (b # mixin));
    END LOOP;
    RETURN result;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- self check:
--   SELECT transform_bytes(transform_bytes('hello world'::bytea, 'abc'::bytea), 'abc'::bytea);
-- returns the original 'hello world'.
