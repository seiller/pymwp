int foo(int X0, int X1){
    X0=1; X1=1;
    while(X1<10){
        X0 = X1*X0;
        X1 = X1+X0;
    }
}
