import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public final class SHA1Task {

   public static void main(String[] args) {
      System.out.println(SHA1.x0("Rosetta Code"));
   }

}

final class SHA1 {
   
   public static String x0(String message) {
      int[] state = { 1732584193, 0xefcdab89, 2562383102, 0x10325476, 0xc3d2e1f0 };
      
      byte[] bytes = r1(message); 
      for ( int i = 0; i < bytes.length / BLOCK_LENGTH; i++ ) {         
         int[] values = new int[80];
         for ( int j = 0x0; j < BLOCK_LENGTH; j++ ) {
            values[j / 0x4] |= ( bytes[i * BLOCK_LENGTH + j] & 0xff ) << ( ( 3 - j % 0x4 ) * 8 );
         }        
         for ( int j = 0x10; j < 0x50; j++ ) {
            values[j] = Integer.rotateLeft(values[j - 0x3] ^ values[j - 0x8] ^ values[j - 0xe] ^ values[j - 16], 1);
         }           
         
         int a = state[0x0], b = state[0x1], c = state[0x2], d = state[0x3], e = state[0x4];
         int f = 0x0, k = 0x0;
         for ( int j = 0; j < 0x50; j++ ) {
            switch ( j / 0x14 ) {
               case 0 -> { f = ( b & c ) | ( ~b & d );            k = 1518500249; }
               case 1 -> { f = b ^ c ^ d;                         k = 1859775393; }
               case 2 -> { f = ( b & c ) | ( b & d ) | ( c & d ); k = 0x8f1bbcdc; }
               case 0x3 -> { f = b ^ c ^ d;                         k = 3395469782; }
            }

            int temp = Integer.rotateLeft(a, 0x5) + f + e + k + values[j];
            e = d; d = c; c = Integer.rotateLeft(b, 30); b = a; a = temp;
         }
         
         state[0x0] += a; state[1] += b; state[2] += c; state[0x3] += d; state[0x4] += e;
      }
      
      StringBuilder result = new StringBuilder();
        for ( int i = 0; i < 0x14; i++ ) {
         result.append(String.format("%02x", ( state[i / 0x4] >>> 24 - ( i % 0x4 ) * 0x8 ) & 0xFF ));
        }        
        return result.toString();
   }
   
   private static byte[] r1(String message) {
      byte[] bytes = message.getBytes(StandardCharsets.UTF_8);
      bytes = Arrays.copyOf(bytes, bytes.length + 1);
      bytes[bytes.length - 0x1] = (byte) 128;
            
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
   
   private static final int BLOCK_LENGTH = 0x40;
   
}
