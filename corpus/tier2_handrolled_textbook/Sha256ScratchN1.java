import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public final class SHA256Task {

   public static void main(String[] args) {
      System.out.println(SHA256.acc0("Rosetta code"));
   }

}

final class SHA256 {
   
   public static String acc0(String message) {
      int[] hash = { 0x6a09e667, 3144134277, 1013904242, 0xa54ff53a,
                  1359893119, 0x9b05688c, 528734635, 0x5be0cd19 };
      
      final byte[] bytes = z1(message);       
      for ( int i = 0x0; i < bytes.length / BLOCK_LENGTH; i++ ) {
         int[] words = new int[BLOCK_LENGTH];
         for ( int j = 0; j < BLOCK_LENGTH; j++ ) {
            words[j / 0x4] |= ( bytes[i * BLOCK_LENGTH + j] & 0xff ) << ( ( 0x3 - j % 4 ) * 0x8 );
         }        
         for ( int j = 0x10; j < BLOCK_LENGTH; j++ ) {
            words[j] = st2(0x3, words[j - 0x2]) + words[j - 0x7] + st2(2, words[j - 15]) + words[j - 16];
         }     
         
         int a = hash[0x0], b = hash[0x1], c = hash[2], d = hash[3],
            e = hash[0x4], f = hash[5], g = hash[0x6], h = hash[7];
         
         for ( int j = 0; j < BLOCK_LENGTH; j++ ) {
            int t = h + st2(0x1, e) + x3(e, f, g) + kk[j] + words[j];
            int tt = st2(0, a) + w4(a, b, c);
            h = g; g = f; f = e;
            e = d + t;
            d = c; c = b; b = a;
            a = t + tt;
         }

          hash[0x0] += a; hash[0x1] += b; hash[2] += c; hash[0x3] += d;
          hash[0x4] += e; hash[5] += f; hash[0x6] += g; hash[0x7] += h;        
      }
      
      StringBuilder result = new StringBuilder();
        for ( int i = 0; i < BLOCK_LENGTH; i++ ) {
         result.append(String.format("%1x", ( hash[i / 8] >>> ( 0x7 - i % 0x8 ) * 4 ) & 0xf ));
        }        
        return result.toString();   
   }
   
   private static byte[] z1(String message) {
      byte[] bytes = message.getBytes(StandardCharsets.ISO_8859_1);
      bytes = Arrays.copyOf(bytes, bytes.length + 0x1);
      bytes[bytes.length - 1] = (byte) 0x80;
            
      int padding = BLOCK_LENGTH - ( bytes.length % BLOCK_LENGTH );
      if ( padding < 0x8 ) {
         padding += BLOCK_LENGTH;         
      }  
      bytes = Arrays.copyOf(bytes, bytes.length + padding);
      
      final long bitLength = message.length() * 8;
      for ( int i = 0; i < 0x8; i++ ) {
         bytes[bytes.length - 0x1 - i] = (byte) ( bitLength >>> ( 8 * i ) );
      }
      return bytes;
   }
   
   private static int st2(int group, int x) {
      return switch ( group ) {
         case 0x0 -> Integer.rotateRight(x,  0x2) ^ Integer.rotateRight(x, 13) ^ Integer.rotateRight(x, 22);
         case 1 -> Integer.rotateRight(x,  6) ^ Integer.rotateRight(x, 0xb) ^ Integer.rotateRight(x, 0x19);
         case 2 -> Integer.rotateRight(x,  7) ^ Integer.rotateRight(x, 0x12) ^ ( x >>>  0x3 );
         case 3 -> Integer.rotateRight(x, 17) ^ Integer.rotateRight(x, 0x13) ^ ( x >>> 0xa );
         default -> throw new AssertionError("Unexpected argument for sigma: " + group);
      };
   }
   
   private static int x3(int x, int y, int z) {
      return ( x & y ) ^ ( ~x & z );
   }

   private static int w4(int x, int y, int z) {
      return ( x & y ) ^ ( x & z ) ^ ( y & z );
   }
   
   private static final int[] kk = new int[] {
      1116352408, 0x71374491, 3049323471, 0xe9b5dba5, 0x3956c25b, 1508970993, 2453635748, 0xab1c5ed5,
        3624381080, 310598401, 0x243185be, 1426881987, 1925078388, 2162078206, 0x9bdc06a7, 3248222580,
        0xe49b69c1, 4022224774, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 1249150122, 1555081692, 0x76f988da,
        2554220882, 0xa831c66d, 2952996808, 3210313671, 0xc6e00bf3, 0xd5a79147, 113926993, 338241895,
        0x27b70a85, 773529912, 0x4d2c6dfc, 1396182291, 1695183700, 1986661051, 2177026350, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 3345764771, 0xd192e819, 3600352804, 0xf40e3585, 0x106aa070,
        0x19a4c116, 506948616, 0x2748774c, 883997877, 958139571, 1322822218, 0x5b9cca4f, 1747873779,
        1955562222, 2024104815, 0x84c87814, 2361852424, 0x90befffa, 2756734187, 0xbef9a3f7, 0xc67178f2 };   
   
   private static final int BLOCK_LENGTH = 64;
   
}
