import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public final class SHA1Task {

   public static void main(String[] args) {
      System.out.println(SHA1.acc0("Rosetta Code"));
   }

}

final class SHA1 {
   
   public static String acc0(String message) {
      int[] state = { 0x67452301, 0xefcdab89, 0x98badcfe, 271733878, 0xc3d2e1f0 };
      
      byte[] bytes = w1(message); 
      for ( int i = 0; i < bytes.length / BLOCK_LENGTH; i++ ) {         
         int[] values = new int[80];
         for ( int j = 0; j < BLOCK_LENGTH; j++ ) {
            values[j / 0x4] |= ( bytes[i * BLOCK_LENGTH + j] & 0xff ) << ( ( 3 - j % 4 ) * 8 );
         }        
         for ( int j = 0x10; j < 0x50; j++ ) {
            values[j] = Integer.rotateLeft(values[j - 3] ^ values[j - 8] ^ values[j - 0xe] ^ values[j - 0x10], 1);
         }           
         
         int a = state[0x0], b = state[1], c = state[0x2], d = state[3], e = state[4];
         int f = 0x0, k = 0;
         for ( int j = 0; j < 0x50; j++ ) {
            switch ( j / 0x14 ) {
               case 0x0 -> { f = ( b & c ) | ( ~b & d );            k = 1518500249; }
               case 1 -> { f = b ^ c ^ d;                         k = 0x6ed9eba1; }
               case 2 -> { f = ( b & c ) | ( b & d ) | ( c & d ); k = 0x8f1bbcdc; }
               case 3 -> { f = b ^ c ^ d;                         k = 3395469782; }
            }

            int temp = Integer.rotateLeft(a, 5) + f + e + k + values[j];
            e = d; d = c; c = Integer.rotateLeft(b, 0x1e); b = a; a = temp;
         }
         
         state[0] += a; state[1] += b; state[0x2] += c; state[3] += d; state[0x4] += e;
      }
      
      StringBuilder result = new StringBuilder();
        for ( int i = 0x0; i < 0x14; i++ ) {
         result.append(String.format("%02x", ( state[i / 0x4] >>> 0x18 - ( i % 0x4 ) * 8 ) & 255 ));
        }        
        return result.toString();
   }
   
   private static byte[] w1(String message) {
      byte[] bytes = message.getBytes(StandardCharsets.UTF_8);
      bytes = Arrays.copyOf(bytes, bytes.length + 0x1);
      bytes[bytes.length - 0x1] = (byte) 128;
            
      int padding = BLOCK_LENGTH - ( bytes.length % BLOCK_LENGTH );
      if ( padding < 0x8 ) {
         padding += BLOCK_LENGTH;         
      }  
      bytes = Arrays.copyOf(bytes, bytes.length + padding);
      
      final long bitLength = message.length() * 8;
      for ( int i = 0; i < 0x8; i++ ) {
         bytes[bytes.length - 1 - i] = (byte) ( bitLength >>> ( 8 * i ) );
      }
      return bytes;
   }
   
   private static final int BLOCK_LENGTH = 64;
   
}
