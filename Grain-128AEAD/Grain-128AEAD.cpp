#include<iostream>
#include<bitset>
#include<fstream>
#include<string.h>
#include<stdlib.h>
enum GRAIN_ROUND {INIT, ADDKEY, NORMAL};
using namespace std;

typedef struct {
	bitset<128> lfsr;
	bitset<128> nfsr;
	bitset<64> auth_acc;//accumulator
	bitset<64> auth_sr;//register
} grain_state;

typedef struct {
	bitset<8> message;
} grain_data;

bitset<128> key;
unsigned int grain_round;

bitset<1> shift(bitset<128> &fsr,bitset<1> s){
	bitset<1> out;
	out[0]=fsr[0];
	fsr>>=1;
	fsr[127]=s[0];
	return out;
}
/*update the content of LFSR*/
bitset<1> next_lfsr_fb(grain_state *grain){
	bitset<1> out;
    out[0]=grain->lfsr[96] ^ grain->lfsr[81] ^ grain->lfsr[70] ^ grain->lfsr[38] ^ grain->lfsr[7] ^ grain->lfsr[0];
	return out;
}
/*update the content of NFSR*/
bitset<1> next_nfsr_fb(grain_state *grain){
	bitset<1> out;
    out[0]=grain->nfsr[96] ^ grain->nfsr[91] ^ grain->nfsr[56] ^ grain->nfsr[26] ^ grain->nfsr[0] ^ (grain->nfsr[84] & grain->nfsr[68]) ^
			(grain->nfsr[67] & grain->nfsr[3]) ^ (grain->nfsr[65] & grain->nfsr[61]) ^ (grain->nfsr[59] & grain->nfsr[27]) ^
			(grain->nfsr[48] & grain->nfsr[40]) ^ (grain->nfsr[18] & grain->nfsr[17]) ^ (grain->nfsr[13] & grain->nfsr[11]) ^
			(grain->nfsr[82] & grain->nfsr[78] & grain->nfsr[70]) ^ (grain->nfsr[25] & grain->nfsr[24] & grain->nfsr[22]) ^
			(grain->nfsr[95] & grain->nfsr[93] & grain->nfsr[92] & grain->nfsr[88]);
	return out;
}
/*preoutput*/
bitset<1> next_h(grain_state *grain){
	#define x0 grain->nfsr[12]	// bi+12
	#define x1 grain->lfsr[8]		// si+8
	#define x2 grain->lfsr[13]	// si+13
	#define x3 grain->lfsr[20]	// si+20
	#define x4 grain->nfsr[95]	// bi+95
	#define x5 grain->lfsr[42]	// si+42
	#define x6 grain->lfsr[60]	// si+60
	#define x7 grain->lfsr[79]	// si+79
	#define x8 grain->lfsr[94]	// si+94

	bitset<1> h_out;
	h_out[0]=(x0 & x1) ^ (x2 & x3) ^ (x4 & x5) ^ (x6 & x7) ^ (x0 & x4 & x8);
	return h_out;
}
bitset<1> next_z(grain_state *grain,bitset<1> keybit,bitset<1> keybit64){
	bitset<1> lfsr_fb=next_lfsr_fb(grain);
	bitset<1> nfsr_fb=next_nfsr_fb(grain);
	bitset<1> h_out=next_h(grain);
	const unsigned int A[]={2, 15, 36, 45, 64, 73, 89};
	bitset<1> temp;
	for(int i=0;i<7;i++){
		temp[0]=temp[0]^grain->nfsr[A[i]];
	}
	bitset<1> y;
	y[0]=h_out[0]^grain->lfsr[93]^temp[0];
	bitset<1> lfsr_out;
	if(grain_round==INIT){
		lfsr_out=shift(grain->lfsr,lfsr_fb^y);
		shift(grain->nfsr,nfsr_fb^lfsr_out^y);
	}
	else if(grain_round==ADDKEY){
		lfsr_out=shift(grain->lfsr,lfsr_fb^y^keybit64);
		shift(grain->nfsr,nfsr_fb^lfsr_out^y^keybit);
	}
	else if(grain_round==NORMAL){
		lfsr_out=shift(grain->lfsr,lfsr_fb);
		shift(grain->nfsr,nfsr_fb^lfsr_out);
	}
	return y;
}
/*initialize the generator*/
void init(grain_state *grain,bitset<128> key,bitset<96> iv){
	for(int i=0;i<128;i++){
		grain->nfsr[i]=key[i];
	}
	for(int i=0;i<96;i++){
		grain->lfsr[i]=iv[i];
	}
	for(int i=96;i<127;i++){
		grain->lfsr.set(i);
	}
	grain->lfsr.set(127,0);
	grain_round=INIT;
	
	for(int i=0;i<320;i++){
		next_z(grain,0,0);
	}
	
	grain_round=ADDKEY;
	for(int i=0;i<64;i++){
		bitset<1> temp;
		temp[0]=key[i];
		bitset<1> temp64;
		temp64[0]=key[i+64];
		next_z(grain,temp,temp64);
	}

	grain_round=NORMAL;
	for(int i=0;i<64;i++){
		grain->auth_acc[i]=(next_z(grain,0,0))[0];
	}
	for(int i=0;i<64;i++){
		grain->auth_sr[i]=(next_z(grain,0,0))[0];
	}
    /*cout<<grain->lfsr<<endl;
    cout<<grain->nfsr<<endl;
    cout<<grain->auth_acc<<endl;
    cout<<grain->auth_sr<<endl;*/
}
/*tranform the plaintext*/
grain_data* init_data(const unsigned char *msg,unsigned long long msg_len){
	grain_data *data=(grain_data*)calloc(msg_len+1,sizeof(grain_data));
	for(auto i=0;i<msg_len;i++){
		for(int j=0;j<8;j++){
			data[i].message[j]=(msg[i]>>j&1);
		}
	}
    return data;
}
void auth_shift(bitset<64> &sr,bitset<1> fb){
	sr>>=1;
	sr[63]=fb[0];
}
void accumulate(grain_state *grain){
	for(int i=0;i<64;i++){
		grain->auth_acc[i]=grain->auth_acc[i] ^ grain->auth_sr[i];
	}
}
/*DER mode*/
grain_data* encode_der(unsigned long long len,int *der_len){
    unsigned long long len_tmp;
    *der_len=0;
	int temp=0;
    grain_data *der;
    if(len<128){
        der=(grain_data*)calloc(1,sizeof(grain_data));
        for(int i=0;i<8;i++){
            der[0].message[i]=((len>>(7-i))&1);
        }
		temp++;
		(*der_len)=temp;
        return der;
    }
    len_tmp=len;
    do{
        len_tmp>>=8;
        temp++;
    }while(len_tmp!=0);
    der=(grain_data*)calloc(temp+1,sizeof(grain_data));
    for(int i=0;i<8;i++){
        der[0].message[i]=(((0x80|temp)>>(7-i))&1);
    }
    len_tmp=len;
    for(int i=temp;i>0;i--){
        for(int j=0;j<8;j++){
            der[i].message[j]=(((len_tmp & 0xff)>>(7-j))&1);
        }
        len_tmp>>=8;
    }
	*(der_len)=temp+1;
    return der;
}
void aead_encrypt(unsigned char *m,unsigned long long mlen,
                unsigned char *ad,unsigned long long adlen,
                bitset<128> k,bitset<96> non)
{
    grain_state grain;
    init(&grain,k,non);
    grain_data *data=NULL;
    if(m!=NULL) data=init_data(m,mlen);
    grain_data *ader=NULL;
    int aderlen=0;
    grain_data *adq=NULL,*temp2;
    temp2=encode_der(adlen,&aderlen);
    ader=(grain_data*)calloc(aderlen+adlen,sizeof(grain_data));
        for(int i=0;i<aderlen;i++){
            ader[i].message=temp2[i].message;
        }

    /*reverse the associated data*/
    if(ad!=NULL){
        adq=(grain_data*)calloc(adlen,sizeof(grain_data));
        for(auto i=0;i<adlen;i++){
            for(int j=0;j<8;j++){
                adq[i].message[j]=(ad[i]>>(7-j)&1);
            }
        }
        for(int i=aderlen;i<aderlen+adlen;i++){
            ader[i].message=adq[i-aderlen].message;
        }
    }
    free(temp2);
    unsigned long long ad_cnt=0;
    bitset<8> adval;
    /*authenticate with no plaintext and update the authenticator*/
    for(unsigned long long i=0;i<aderlen+adlen;i++){
        for(int j=0;j<16;j++){
            bitset<1> z_next=next_z(&grain,0,0);
            if(j%2==0){
                //continue;
            }
            else{
                bitset<8> temp;
                temp.set(7-(ad_cnt%8));
                adval=(ader[ad_cnt/8].message)&temp;
                if(adval.any()){
                    accumulate(&grain);
                }
                auth_shift(grain.auth_sr,z_next);
                ad_cnt++;
            }
        }
    }
    unsigned long long ac_cnt=0,m_cnt=0,c_cnt=0,c_len=0;
    bitset<8> cc;
    grain_data *c;
    c=(grain_data*)calloc(mlen+8,sizeof(grain_data));
    for(unsigned long long i=0;i<mlen;i++){
        cc.reset();
        for(int j=0;j<16;j++){
            bitset<1> z_next=next_z(&grain,0,0);
            if(j%2==0){
                cc[c_cnt%8]=cc[c_cnt%8]|(data[i].message[m_cnt%8]^z_next[0]);
                m_cnt++;
                c_cnt++;
            }
            else{
                if(data[i].message[ac_cnt%8]==1){
                    accumulate(&grain);
                }
                ac_cnt++;
                auth_shift(grain.auth_sr,z_next);
            }
        }
        c[i].message=cc;
        c_len++;
    }
    next_z(&grain,0,0);
    
    accumulate(&grain);
    /*add the TAG to the ciphertext*/
    unsigned long long acc_idx=0;
    for(unsigned long long i=mlen;i<mlen+8;i++){
        bitset<8> temp;
        temp.reset();
        for(int j=0;j<8;j++){
            temp[j]=temp[j]|grain.auth_acc[8*acc_idx+j];
        }
        c[i].message=temp;
        acc_idx++;
        c_len++;
    }
    cout<<"The ciphertext is(hexadecimal):";
    for(int i=0;i<mlen+8;i++){
        unsigned char val=0;
        for(int j=7;j>=0;j--){
            val|=(c[i].message[j]&1)<<j;
        }
        printf("%02x",val);
    }
    cout<<endl;
    if(ader!=NULL) free(ader);
    if(data!=NULL) free(data);
    if(adq!=NULL) free(adq);
    
}
int main(){
    bitset<128> k;
    bitset<96> iv;
    //char key[16]={0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f};
    //char nonce[12]={0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b};
    //char key[16]={0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
    //char nonce[12]={0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
    string key;
    string nonce;
    string plaintxt;
    string ascd;
    bool flag;
    unsigned char *ad=NULL;
    unsigned char *m=NULL;
    unsigned long long adlen=0;
    unsigned long long mlen=0;
    cout<<"choose entryption with plaintext or null(1 or 0):";
    cin>>flag;
    if(flag){
    cout<<"Enter the words you want to encrypt:"<<endl;
    cin>>plaintxt;
    m=(unsigned char*)calloc(plaintxt.length(),sizeof(unsigned char));
    for(int i=0;i<plaintxt.length();i++) m[i]=plaintxt[i];
    mlen=plaintxt.length();
    }
    cout<<"Enter a 128 bits key:";
    cin>>key;
    cout<<"Enter a 96 bits nonce:";
    cin>>nonce;
    bool f;
    cout<<"whether to need associated data(1 or 0):";
    cin>>f;
    if(f){
        cout<<"Enter your data:";
        cin>>ascd;
        ad=(unsigned char*)calloc(ascd.length(),sizeof(unsigned char));
        for(int i=0;i<ascd.length();i++) ad[i]=ascd[i];
        adlen=ascd.length();
    }
    
    int temp=key.length()<=16?key.length():16;
    for(int i=0;i<temp;i++){
        for(int j=0;j<8;j++){
            k[i*8+j]=key[i]>>j&1;
        }
    }
    temp=nonce.length()<=12?nonce.length():12;
    for(int i=0;i<temp;i++){
        for(int j=0;j<8;j++){
            iv[i*8+j]=nonce[i]>>j&1;
        }
    }
    grain_state grain;
    aead_encrypt(m,mlen,ad,adlen,k,iv);
    return 0;
}