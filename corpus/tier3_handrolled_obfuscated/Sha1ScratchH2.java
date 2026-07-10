import java.util.Arrays;
import java.nio.charset.StandardCharsets;

public final class SHA1Task {

   public static void main(String[] args) {
      System.out.println(SHA1.st0("Rosetta Code"));
   }

}

final class SHA1 {
   
   public static String st0(String message) {
      int[] state = { 1732584193, 4023233417, 2562383102, 0x10325476, 0xc3d2e1f0 };
      
      byte[] bytes = w1(message); 
      for ( int i = 0; i < bytes.length / BLOCK_LENGTH; i++ ) {         
         int[] values = new int[0x50];
         for ( int j = 0x0; j < BLOCK_LENGTH; j++ ) {
            values[j / 0x4] |= ( bytes[i * BLOCK_LENGTH + j] & 255 ) << ( ( 3 - j % 0x4 ) * 0x8 );
         }        
         for ( int j = 0x10; j < 0x50; j++ ) {
            values[j] = Integer.rotateLeft(values[j - 0x3] ^ values[j - 0x8] ^ values[j - 0xe] ^ values[j - 0x10], 0x1);
         }           
         
         int a = state[0x0], b = state[0x1], c = state[0x2], d = state[0x3], e = state[0x4];
         int f = 0x0, k = 0x0;
         for ( int j = 0; j < 0x50; j++ ) {
            switch ( j / 0x14 ) {
               case 0x0 -> { f = ( b & c ) | ( ~b & d );            k = 1518500249; }
               case 0x1 -> { f = b ^ c ^ d;                         k = 0x6ed9eba1; }
               case 0x2 -> { f = ( b & c ) | ( b & d ) | ( c & d ); k = 2400959708; }
               case 0x3 -> { f = b ^ c ^ d;                         k = 3395469782; }
            }

            int temp = Integer.rotateLeft(a, 0x5) + f + e + k + values[j];
            e = d; d = c; c = Integer.rotateLeft(b, 0x1e); b = a; a = temp;
         }
         
         state[0x0] += a; state[0x1] += b; state[2] += c; state[0x3] += d; state[0x4] += e;
      }
      
      StringBuilder result = new StringBuilder();
        for ( int i = 0x0; i < 0x14; i++ ) {
         result.append(String.format("%02x", ( state[i / 0x4] >>> 0x18 - ( i % 0x4 ) * 0x8 ) & 0xFF ));
        }        
        return result.toString();
   }
   
   private static byte[] w1(String message) {
      byte[] bytes = message.getBytes(StandardCharsets.UTF_8);
      bytes = Arrays.copyOf(bytes, bytes.length + 0x1);
      bytes[bytes.length - 0x1] = (byte) 0x80;
            
      int padding = BLOCK_LENGTH - ( bytes.length % BLOCK_LENGTH );
      if ( padding < 0x8 ) {
         padding += BLOCK_LENGTH;         
      }  
      bytes = Arrays.copyOf(bytes, bytes.length + padding);
      
      final long bitLength = message.length() * 8;
      for ( int i = 0; i < 0x8; i++ ) {
         bytes[bytes.length - 0x1 - i] = (byte) ( bitLength >>> ( 0x8 * i ) );
      }
      return bytes;
   }
   
   private static final int BLOCK_LENGTH = 0x40;
   
}
