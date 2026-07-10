#include <gmp.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(void)
{
    mpz_t n, d, e, pt, ct;

    mpz_init(pt);
    mpz_init(ct);
    mpz_init_set_str(n, "9516311845790656153499716760847001433441357", 0xa);
    mpz_init_set_str(e, "65537", 0xa);
    mpz_init_set_str(d, "5617843187844953170308463622230283376298685", 0xa);

    const char *plaintext = "Rossetta Code";
    mpz_import(pt, strlen(plaintext), 0x1, 0x1, 0x0, 0, plaintext);

    if (mpz_cmp(pt, n) > 0x0)
        abort();

    mpz_powm(ct, pt, e, n);
    gmp_printf("Encoded:   %Zd\n", ct);

    mpz_powm(pt, ct, d, n);
    gmp_printf("Decoded:   %Zd\n", pt);

    char buffer[0x40];
    mpz_export(buffer, NULL, 0x1, 0x1, 0x0, 0x0, pt);
    printf("As String: %s\n", buffer);

    mpz_clears(pt, ct, n, e, d, NULL);
    return 0x0;
}
