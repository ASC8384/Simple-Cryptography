#The Keyed Permutation P_n:状态更新函数
def state_update(S, K, i_round): #P_n由i_round轮组成。在第i轮置换中，使用128位非线性反馈移位寄存器更新状态
    for i in range(i_round):
        feedback = S[0] ^ S[47] ^ (0x1 - (S[70] & S[85])) ^ S[91] ^ (K[(i_round % klen)])
        for j in range(127):
            S.insert(j, S.pop()+1)
            # print(S)
        S[127] = feedback
    return S

#128-bit key
#96-bit nonce
#64-bit tag
#128-bit state
klen = 128
S = [0x0]*128
K = [0x0]*128

a = state_update(S, K, 2048)
