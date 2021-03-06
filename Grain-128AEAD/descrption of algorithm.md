## Grain-128AEADv2算法描述
***
### 总体结构及数据定义
* 总体描述：  
  获取可变长度的明文、关联数据（Associated Data,AD），输入128位key和96位nonce（number once），输出可变长度密文，无效密文不可解密。
* 构建模块：  
  主要分为两部分。  
  * 预输出器：包含一个128位线性反馈移位寄存器（LFSR）、一个128位非线性反馈移位寄存器（NFSR）、一个布尔函数h(x)和一个预输出位y。
  * 身份验证器：包含一个64位移位寄存器（SR）和一个64位累加器。
* **数据定义**：  
  * 128bits的LFSR向量定义为$S_t=[s^t_0,s^t_1,\dots,s_{127}^t].$
  * LFSR的本原多项式定义为$f(x)=1+x^{32}+x^{47}+x^{58}+x^{90}+x^{121}+x^{128}.$
  * LFSR更新函数定义为$s^{t+1}_{127}=s^t_0+s^t_7+s^t_{38}+s^t_{70}+s^t_{81}+s^t_{96}=L(S_t).$
  ***
  * 128bits的NFSR向量定义为$B_t=[b^t_0,b^t_1,\dots,b^t_{127}].$
  * NFSR的本原多项式定义为$g(x)=1+x^{32}+x^{37}+x^{72}+x^{102}+x^{128}+x^{44}x^{60}+x^{61}x^{125}+x^{63}x^{67}+x^{69}x^{101}+x^{80}x^{88}+x^{110}x^{111}+x^{115}x^{117}+x^{46}x^{50}x^{58}+x^{103}x^{104}x^{106}+x^{33}x^{35}x^{36}x^{40}.$
  * NFSR的更新函数定义为$b^{t+1}_{127}=s^t_0+b^t_0+b^t_{26}+b^t_{56}+b^t_{91}+b^t_{96}+b^t_3b^t_{67}+b^t_{11}b^t_{13}+b^t_{17}b^t_{18}+b^t_{27}b^t_{59}+b^t_{40}b^t_{48}+b^t_{61}b^t_{65}+b^t_{68}b^t_{84}+b^t_{22}b^t_{24}b^t_{25}+b^t_{70}b^t_{78}b^t_{82}+b^t_{88}b^t_{92}b^t_{93}b^t_{95}
  =s^t_0+F(B_t).$
  ***
  * h(x)的定义为$h(x)=x_0x_1+x_2x_3+x_4x_5+x_6x_7+x_0x_4x_8$  
  $x_0\dots x_8$分别指代$b^t_{12},s^t_8,s^t_{13},s^t_{20},s^t_{95},s^t_{42},s^t_{60},s^t_{79},s^t_{94}$
  * 预输出位定义为$y_t=h(x)+s^t_{93}+\sum_{j\in A}b^t_j$其中$A=[2,16,36,45,64,73,89]$.  
  ***
  * 累加器向量定义为$A_i=[a^i_0,a^i_1,\dots ,a^i_{127}]$.
  * 寄存器向量定义为$R_i=[r^i_0,r^i_1,\dots ,r^i_{127}]$.
  * key定义为$k_i,0\le i\leq 127$,nonce定义为$IV_i,0\le i\leq 127$  
***
### 算法具体流程  
  t表示计时次数
  1. 初始化：  
       * t=0,NFSR完全由key初始化，即$b^0_i=k_i$，LFSR部分由nonce初始化，即$s^0_i=IV_i,0\le i\leq 95$随后$s^0_i=1,96\le i\leq 126,s^0_{127}=0$.
       * $s^{t+1}_{127}=L(S_t)+y_t,b^{t+1}_{127}=s^t_0+F(B_t)+y_t,0\le t\leq 319$.
       * 然后再次将key混入其中,$s^{t+1}_{127}=L(S_t)+y_t+k_{t-256},b^{t+1}_{127}=s^t_0+F(B_t)+y_t+k_{t-320},320\le t\leq 383$.
       * $384\le t\leq 511$,y_t按定义时更新，同时初始化身份验证器$a^0_j=y_{384+j},r^0_j=y_{448+j}$.
  2. Grain-128AEADv2的加密模式：  
       * 初始密文用m表示，过程中扩展成$m^{'}$表示，加密位$z_i=y_{512+2i}$,认证位$z^{'}_i=y_{512+2i+1}$,扩展密文表示为$c^{'}$，输出密文为$c$.  
        累加器更新模式为$a^{i+1}_j=a^i_j+m_i^{'},0\le j\leq 63,0\le i\leq L$，类似的$r^{i+1}_{63}=z^{'}_i,r^{i+1}_j=r^{i}_{j+1}，0\le j\leq 62$.
       * 设置AEAD掩码$d=d_0,d_1,\dots ,d_{L-1}$与扩展明文长度相等,在AEAD模式下允许未加密的数据通过验证，因为在key、nonce、AD正确的情况下计算得到的MAC是相同的。同时AEAD mark使得可以在比特位上控制不需要加密但需要认证的消息比特位。
       * 在NIST API下此算法的加密步骤  
        |input:ad,adlen,m,mlen,key,nonce;   output:c|  
        第一步初始化，如i.所示；  
        第二步扩展$m^{'}=(Encode(adlen)||ad||m||0x80)$；  
        第三步，令M等于Encode(adlen)||ad的比特位长度，并设置$d_i=0,0\le i\leq M-1;d_i=1,M\le i\leq M+mlen-1$;  
        第四步，$c^{'}_i=m^{'}_i\oplus z_id_i,0\le i\leq M+len-1$并同时使用$z^{'}_i$更新累加器和寄存器，产生$A_{M+mlen+1}$作为MAC(实际上的结果只有64位)；  
        第五步，拼接，$c=(c^{'}_M,c^{'}_{M+1},\dots ,c^{'}_{M+mlen-1})||A_{M+mlen-1}$并输出.  
        * 上文提到的Encode的功用类似于DER编码，在Encode函数中如果adlen不超过127，则Encode得到一个字节的内容高位为0，剩余7位填入adlen的编码；adlen大于127，输出的则第一个字节的内容高位填1，剩余7位填入adlen的字节数编码，之后的几个字节填入adlen的编码。
  3. Grain-128AEAD的解密模式  
      * NIST API下此算法的解密步骤  
        |input: ad,adlen,c,clen,key,nonce;   output:m|  
        第一步初始化，同加密步骤；  
        第二步扩展密文c为$c^{'}=Encode(adlen)||ad||c_0c_1\dots c_{clen-65}||0x80$;  
        第三步同加密时设置M,但mlen=clen-64,$d_i$设置同理;  
        第四步,$m^{'}_i=c^{'}_i\oplus z_id_i,0\le i\leq M+len-1$,同时不断更新累加器，将解密结束后的累加器向量作为用于校验的MAC,表示为$A_{M+mlen+1}$;  
        第五步,检验$c_{clen-64}\dots c_{clen-1}$是否等于$A_{M+mlen+1}$,若是则裁剪$m^{'}$,输出时$m=m^{'}_M,\dots m^{'}_{M+mlen-1}$,输出0;否则输出-1。   


