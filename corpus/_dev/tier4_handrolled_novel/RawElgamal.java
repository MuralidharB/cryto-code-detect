import java.math.BigInteger;
import java.util.Random;

public class RawElgamal {
    final BigInteger p, g, x, y;
    final Random rnd = new Random(7);

    RawElgamal(BigInteger p, BigInteger g, BigInteger x) {
        this.p = p; this.g = g; this.x = x;
        this.y = g.modPow(x, p);
    }

    BigInteger[] encrypt(BigInteger m) {
        BigInteger k = new BigInteger(p.bitLength() - 1, rnd).mod(p.subtract(BigInteger.TWO)).add(BigInteger.ONE);
        BigInteger c1 = g.modPow(k, p);
        BigInteger s = y.modPow(k, p);
        BigInteger c2 = m.multiply(s).mod(p);
        return new BigInteger[]{c1, c2};
    }

    BigInteger decrypt(BigInteger c1, BigInteger c2) {
        BigInteger s = c1.modPow(x, p);
        BigInteger sInv = s.modInverse(p);
        return c2.multiply(sInv).mod(p);
    }

    public static void main(String[] args) {
        BigInteger p = BigInteger.valueOf(2357);
        BigInteger g = BigInteger.valueOf(2);
        BigInteger x = BigInteger.valueOf(1751);
        RawElgamal e = new RawElgamal(p, g, x);
        BigInteger m = BigInteger.valueOf(1234);
        BigInteger[] c = e.encrypt(m);
        System.out.println("m=" + m + " dec=" + e.decrypt(c[0], c[1]));
    }
}
