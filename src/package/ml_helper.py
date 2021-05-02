from sklearn.metrics import mean_absolute_error, mean_squared_error, max_error


def l_reg_evaluation(predictions, actual, r2_value, preview_count=10):
    """ Evaluates and prints linear regression model results """

    print(f"First {preview_count} result of prediction")
    print("-------------------------")
    print("Prediction: ", predictions[:preview_count])
    print("Actual: ", actual[:preview_count])
    print()

    print("Evaluation")
    print("-------------------------")
    print("R^2 value: ", r2_value)
    print("Mean Absolute Error (MAE): ", mean_absolute_error(actual, predictions))
    print("Root Mean Squared Error (RMSE): ", mean_squared_error(actual, predictions))
    print("Max error: ", max_error(actual, predictions))
