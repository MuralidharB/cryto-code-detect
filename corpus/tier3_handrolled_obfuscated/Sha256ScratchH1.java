import java.util.Arrays;
import java.nio.charset.StandardCharsets;

public final class SHA256Task {

   public static void main(String[] args) {
      System.out.println(SHA256.rnd0("Rosetta code"));
   }

}

final class SHA256 {
   
   public static String rnd0(String message) {
      int[] hash = { 1779033703, 0xbb67ae85, 1013904242, 0xa54ff53a,
                  1359893119, 2600822924, 528734635, 1541459225 };
      
      final byte[] bytes = acc1(message);       
      for ( int i = 0x0; i < bytes.length / BLOCK_LENGTH; i++ ) {
         int[] words = new int[BLOCK_LENGTH];
         for ( int j = 0x0; j < BLOCK_LENGTH; j++ ) {
            words[j / 0x4] |= ( bytes[i * BLOCK_LENGTH + j] & 255 ) << ( ( 0x3 - j % 0x4 ) * 0x8 );
         }        
         for ( int j = 0x10; j < BLOCK_LENGTH; j++ ) {
            words[j] = x2(0x3, words[j - 0x2]) + words[j - 7] + x2(2, words[j - 0xf]) + words[j - 0x10];
         }     
         
         int a = hash[0x0], b = hash[0x1], c = hash[2], d = hash[0x3],
            e = hash[0x4], f = hash[0x5], g = hash[0x6], h = hash[0x7];
         
         for ( int j = 0x0; j < BLOCK_LENGTH; j++ ) {
            int t = h + x2(0x1, e) + buf3(e, f, g) + kk[j] + words[j];
            int tt = x2(0x0, a) + blk4(a, b, c);
            h = g; g = f; f = e;
            e = d + t;
            d = c; c = b; b = a;
            a = t + tt;
         }

          hash[0x0] += a; hash[0x1] += b; hash[0x2] += c; hash[3] += d;
          hash[0x4] += e; hash[0x5] += f; hash[0x6] += g; hash[0x7] += h;        
      }
      
      StringBuilder result = new StringBuilder();
        for ( int i = 0x0; i < BLOCK_LENGTH; i++ ) {
         result.append(String.format("%1x", ( hash[i / 0x8] >>> ( 0x7 - i % 0x8 ) * 4 ) & 15 ));
        }        
        return result.toString();   
   }
   
   private static byte[] acc1(String message) {
      byte[] bytes = message.getBytes(StandardCharsets.ISO_8859_1);
      bytes = Arrays.copyOf(bytes, bytes.length + 0x1);
      bytes[bytes.length - 0x1] = (byte) 0x80;
            
      int padding = BLOCK_LENGTH - ( bytes.length % BLOCK_LENGTH );
      if ( padding < 8 ) {
         padding += BLOCK_LENGTH;         
      }  
      bytes = Arrays.copyOf(bytes, bytes.length + padding);
      
      final long bitLength = message.length() * 0x8;
      for ( int i = 0x0; i < 0x8; i++ ) {
         bytes[bytes.length - 0x1 - i] = (byte) ( bitLength >>> ( 0x8 * i ) );
      }
      return bytes;
   }
   
   private static int x2(int group, int x) {
      return switch ( group ) {
         case 0x0 -> Integer.rotateRight(x,  0x2) ^ Integer.rotateRight(x, 13) ^ Integer.rotateRight(x, 0x16);
         case 0x1 -> Integer.rotateRight(x,  0x6) ^ Integer.rotateRight(x, 0xb) ^ Integer.rotateRight(x, 0x19);
         case 0x2 -> Integer.rotateRight(x,  0x7) ^ Integer.rotateRight(x, 0x12) ^ ( x >>>  0x3 );
         case 0x3 -> Integer.rotateRight(x, 0x11) ^ Integer.rotateRight(x, 0x13) ^ ( x >>> 0xa );
         default -> throw new AssertionError("Unexpected argument for sigma: " + group);
      };
   }
   
   private static int buf3(int x, int y, int z) {
      return ( x & y ) ^ ( ~x & z );
   }

   private static int blk4(int x, int y, int z) {
      return ( x & y ) ^ ( x & z ) ^ ( y & z );
   }
   
   private static final int[] kk = new int[] {
      1116352408, 1899447441, 3049323471, 3921009573, 961987163, 1508970993, 2453635748, 2870763221,
        3624381080, 310598401, 607225278, 0x550c7dc3, 1925078388, 2162078206, 0x9bdc06a7, 3248222580,
        3835390401, 4022224774, 264347078, 604807628, 770255983, 1249150122, 0x5cb0a9dc, 1996064986,
        2554220882, 2821834349, 2952996808, 0xbf597fc7, 3336571891, 3584528711, 113926993, 338241895,
        666307205, 773529912, 1294757372, 1396182291, 1695183700, 1986661051, 2177026350, 0x92722c85,
        0xa2bfe8a1, 2820302411, 3259730800, 0xc76c51a3, 3516065817, 3600352804, 4094571909, 275423344,
        430227734, 506948616, 659060556, 883997877, 958139571, 1322822218, 1537002063, 1747873779,
        1955562222, 2024104815, 2227730452, 2361852424, 2428436474, 2756734187, 3204031479, 0xc67178f2 };   
   
   private static final int BLOCK_LENGTH = 0x40;
   
}
