from sklearn import datasets

# just some example code

iris = datasets.load_iris()

X = iris.data
y = iris.target

print(X, y)
