import java.math.BigInteger;

public class RawRsaPlain {
    final BigInteger n, e, d;

    RawRsaPlain(BigInteger p, BigInteger q, BigInteger e) {
        this.n = p.multiply(q);
        BigInteger phi = p.subtract(BigInteger.ONE).multiply(q.subtract(BigInteger.ONE));
        this.e = e;
        this.d = e.modInverse(phi);
    }

    BigInteger encrypt(BigInteger m) {
        return m.modPow(e, n);
    }

    BigInteger decrypt(BigInteger c) {
        return c.modPow(d, n);
    }

    public static void main(String[] args) {
        BigInteger p = BigInteger.valueOf(61);
        BigInteger q = BigInteger.valueOf(53);
        BigInteger e = BigInteger.valueOf(17);
        RawRsaPlain rsa = new RawRsaPlain(p, q, e);
        BigInteger m = BigInteger.valueOf(65);
        BigInteger c = rsa.encrypt(m);
        System.out.println("c=" + c + " m=" + rsa.decrypt(c));
    }
}
