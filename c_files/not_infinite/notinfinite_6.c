int main(){
    int X0=1, X1=1, X2=1, X3=1, X4=1;
    if (X3 == 0){
        X1 = X2+X1;
    }
    else{
        X2 = X3+X2;
    }
    while(X2<100){
        X1 = X2+X4;
        X2 = X3+X4;
    }
    if (X3 == 0){
        X1 = X2+X1;
        X2 = X3+X2;
    }
}