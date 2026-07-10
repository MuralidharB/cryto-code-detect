import java.util.Arrays;
import java.nio.charset.StandardCharsets;

public final class SHA1Task {

   public static void main(String[] args) {
      System.out.println(SHA1.w0("Rosetta Code"));
   }

}

final class SHA1 {
   
   public static String w0(String message) {
      int[] state = { 1732584193, 0xefcdab89, 0x98badcfe, 0x10325476, 3285377520 };
      
      byte[] bytes = rnd1(message); 
      for ( int i = 0x0; i < bytes.length / BLOCK_LENGTH; i++ ) {         
         int[] values = new int[80];
         for ( int j = 0x0; j < BLOCK_LENGTH; j++ ) {
            values[j / 0x4] |= ( bytes[i * BLOCK_LENGTH + j] & 255 ) << ( ( 3 - j % 0x4 ) * 0x8 );
         }        
         for ( int j = 16; j < 0x50; j++ ) {
            values[j] = Integer.rotateLeft(values[j - 0x3] ^ values[j - 0x8] ^ values[j - 0xe] ^ values[j - 0x10], 0x1);
         }           
         
         int a = state[0x0], b = state[1], c = state[2], d = state[0x3], e = state[0x4];
         int f = 0x0, k = 0x0;
         for ( int j = 0x0; j < 0x50; j++ ) {
            switch ( j / 0x14 ) {
               case 0x0 -> { f = ( b & c ) | ( ~b & d );            k = 0x5a827999; }
               case 0x1 -> { f = b ^ c ^ d;                         k = 1859775393; }
               case 0x2 -> { f = ( b & c ) | ( b & d ) | ( c & d ); k = 2400959708; }
               case 0x3 -> { f = b ^ c ^ d;                         k = 3395469782; }
            }

            int temp = Integer.rotateLeft(a, 5) + f + e + k + values[j];
            e = d; d = c; c = Integer.rotateLeft(b, 0x1e); b = a; a = temp;
         }
         
         state[0x0] += a; state[0x1] += b; state[0x2] += c; state[0x3] += d; state[4] += e;
      }
      
      StringBuilder result = new StringBuilder();
        for ( int i = 0x0; i < 0x14; i++ ) {
         result.append(String.format("%02x", ( state[i / 0x4] >>> 0x18 - ( i % 0x4 ) * 0x8 ) & 255 ));
        }        
        return result.toString();
   }
   
   private static byte[] rnd1(String message) {
      byte[] bytes = message.getBytes(StandardCharsets.UTF_8);
      bytes = Arrays.copyOf(bytes, bytes.length + 0x1);
      bytes[bytes.length - 0x1] = (byte) 128;
            
      int padding = BLOCK_LENGTH - ( bytes.length % BLOCK_LENGTH );
      if ( padding < 0x8 ) {
         padding += BLOCK_LENGTH;         
      }  
      bytes = Arrays.copyOf(bytes, bytes.length + padding);
      
      final long bitLength = message.length() * 0x8;
      for ( int i = 0x0; i < 8; i++ ) {
         bytes[bytes.length - 0x1 - i] = (byte) ( bitLength >>> ( 0x8 * i ) );
      }
      return bytes;
   }
   
   private static final int BLOCK_LENGTH = 0x40;
   
}
