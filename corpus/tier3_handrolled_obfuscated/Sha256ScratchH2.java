import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public final class SHA256Task {

   public static void main(String[] args) {
      System.out.println(SHA256.w0("Rosetta code"));
   }

}

final class SHA256 {
   
   public static String w0(String message) {
      int[] hash = { 1779033703, 3144134277, 1013904242, 2773480762,
                  0x510e527f, 2600822924, 0x1f83d9ab, 1541459225 };
      
      final byte[] bytes = h01(message);       
      for ( int i = 0x0; i < bytes.length / BLOCK_LENGTH; i++ ) {
         int[] words = new int[BLOCK_LENGTH];
         for ( int j = 0x0; j < BLOCK_LENGTH; j++ ) {
            words[j / 0x4] |= ( bytes[i * BLOCK_LENGTH + j] & 255 ) << ( ( 0x3 - j % 0x4 ) * 0x8 );
         }        
         for ( int j = 0x10; j < BLOCK_LENGTH; j++ ) {
            words[j] = acc2(0x3, words[j - 0x2]) + words[j - 0x7] + acc2(0x2, words[j - 0xf]) + words[j - 0x10];
         }     
         
         int a = hash[0x0], b = hash[0x1], c = hash[2], d = hash[0x3],
            e = hash[0x4], f = hash[0x5], g = hash[0x6], h = hash[0x7];
         
         for ( int j = 0x0; j < BLOCK_LENGTH; j++ ) {
            int t = h + acc2(0x1, e) + v3(e, f, g) + kk[j] + words[j];
            int tt = acc2(0x0, a) + x4(a, b, c);
            h = g; g = f; f = e;
            e = d + t;
            d = c; c = b; b = a;
            a = t + tt;
         }

          hash[0x0] += a; hash[0x1] += b; hash[0x2] += c; hash[0x3] += d;
          hash[4] += e; hash[0x5] += f; hash[0x6] += g; hash[0x7] += h;        
      }
      
      StringBuilder result = new StringBuilder();
        for ( int i = 0; i < BLOCK_LENGTH; i++ ) {
         result.append(String.format("%1x", ( hash[i / 0x8] >>> ( 0x7 - i % 0x8 ) * 0x4 ) & 0xf ));
        }        
        return result.toString();   
   }
   
   private static byte[] h01(String message) {
      byte[] bytes = message.getBytes(StandardCharsets.ISO_8859_1);
      bytes = Arrays.copyOf(bytes, bytes.length + 0x1);
      bytes[bytes.length - 0x1] = (byte) 128;
            
      int padding = BLOCK_LENGTH - ( bytes.length % BLOCK_LENGTH );
      if ( padding < 0x8 ) {
         padding += BLOCK_LENGTH;         
      }  
      bytes = Arrays.copyOf(bytes, bytes.length + padding);
      
      final long bitLength = message.length() * 0x8;
      for ( int i = 0; i < 0x8; i++ ) {
         bytes[bytes.length - 0x1 - i] = (byte) ( bitLength >>> ( 0x8 * i ) );
      }
      return bytes;
   }
   
   private static int acc2(int group, int x) {
      return switch ( group ) {
         case 0x0 -> Integer.rotateRight(x,  0x2) ^ Integer.rotateRight(x, 0xd) ^ Integer.rotateRight(x, 0x16);
         case 0x1 -> Integer.rotateRight(x,  0x6) ^ Integer.rotateRight(x, 0xb) ^ Integer.rotateRight(x, 0x19);
         case 2 -> Integer.rotateRight(x,  0x7) ^ Integer.rotateRight(x, 0x12) ^ ( x >>>  0x3 );
         case 0x3 -> Integer.rotateRight(x, 0x11) ^ Integer.rotateRight(x, 0x13) ^ ( x >>> 10 );
         default -> throw new AssertionError("Unexpected argument for sigma: " + group);
      };
   }
   
   private static int v3(int x, int y, int z) {
      return ( x & y ) ^ ( ~x & z );
   }

   private static int x4(int x, int y, int z) {
      return ( x & y ) ^ ( x & z ) ^ ( y & z );
   }
   
   private static final int[] kk = new int[] {
      1116352408, 1899447441, 3049323471, 3921009573, 961987163, 1508970993, 2453635748, 2870763221,
        3624381080, 310598401, 607225278, 1426881987, 0x72be5d74, 2162078206, 2614888103, 3248222580,
        0xe49b69c1, 4022224774, 264347078, 604807628, 770255983, 1249150122, 1555081692, 1996064986,
        2554220882, 2821834349, 2952996808, 3210313671, 3336571891, 3584528711, 113926993, 338241895,
        666307205, 773529912, 1294757372, 1396182291, 1695183700, 0x766a0abb, 0x81c2c92e, 2456956037,
        2730485921, 2820302411, 3259730800, 3345764771, 3516065817, 3600352804, 4094571909, 275423344,
        0x19a4c116, 506948616, 659060556, 0x34b0bcb5, 958139571, 1322822218, 1537002063, 1747873779,
        1955562222, 2024104815, 2227730452, 0x8cc70208, 0x90befffa, 2756734187, 3204031479, 3329325298 };   
   
   private static final int BLOCK_LENGTH = 0x40;
   
}
