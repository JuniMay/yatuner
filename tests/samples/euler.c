#define endl '\n'
#define LL long long
#define L unsigned long long
#define I unsigned int

#include "stdio.h"
L prime[10 * 10000000 + 5];
L visit[10 * 10000000 + 5];

void work() {
    visit[1] = 1;
    for (L i = 2; i <= 10 * 10000000 + 5 - 1; i++) {
        if (!visit[i])
            prime[++prime[0]] = i;
        for (L j = 1; j <= prime[0] && i * prime[j] <= 10 * 10000000 + 5 - 1;
             j++) {
            visit[i * prime[j]] = 1;
            if (i % prime[j] == 0)
                break;
        }
        continue;
    }
    for (L i = 1; i <= 10 * 10000000 + 5 - 1; i++)
        if (!visit[i])
            printf("%d ", i);

    return;
}

int main() {
    work();
    return 0;
}