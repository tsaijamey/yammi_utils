import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline

n_dots=20

X=np.linspace(-2*np.pi,2*np.pi,n_dots)#生成-2*3.14到2*3.14的200个数
Y=np.sin(X)+0.2*np.random.rand(n_dots)-0.1#将X正弦化，然后加入噪音

print(X)
print(Y)
X=X.reshape(-1,1)#扁平化，就是features只能为1
Y=Y.reshape(-1,1)

print(X)
print(Y)

def polynomial_model(degree=1):
    polynomial_features=PolynomialFeatures(degree=degree,include_bias=False)#生成degree阶多项式
    linear_regression=LinearRegression(normalize=True)#线性回归实例化，并且正规化
    pipeline=Pipeline([("polynomial_features",polynomial_features),("linear_regression",linear_regression)])#流水线
    return pipeline


from sklearn.metrics import mean_squared_error

degrees=[2,3,5,10]#多项式的阶数
results=[]#结果数组
for d in degrees:#运行四次
    model=polynomial_model(degree=d)#生产degree多项式模型
    model.fit(X,Y)#将X,Y扔到模型里面去训练
    train_score=model.score(X,Y)#得到评分
    mse=mean_squared_error(Y,model.predict(X))#计算均方根误差
    results.append({"model":model,"degree":d,"score":train_score,"mse":mse})#追加对应数据到results里面
for r in results:
    print("degree:{};train score:{};mean squared error:{}".format(r["degree"],r["score"],r["mse"]))
