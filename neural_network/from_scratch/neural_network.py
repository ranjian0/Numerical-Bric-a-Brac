"""
@author: Vincent Bonnet
@description : Neural network utilities
"""

'''
#CONVENTIONS#

num_inputs : number of inputs on the logistic regression
num_examples : number of examples used for the training
|Array Name   |  Array Shape               | Description                      |
|-------------|----------------------------|----------------------------------|
|w            | (num_inputs, 1)            | input weights                    |
|b            | (1,1)                      | input bias                       |
|y_hat        | (1, num_examples)          | activation per examples          |
|y            | (1, num_examples)          |                                  |
|X            | (num_inputs, num_examples) | training data stored into column |

|Function Name | Description                                   |
|--------------|-----------------------------------------------|
|sigma         | activation function (sigmoid, tanh, Relu ...) |
|L(y_hat, y)   | error function (cross_entropy, ...)           |
'''

import numpy as np
import matplotlib.pyplot as plt

'''
Activation functions
'''
def sigmoid_activation(z):
    return 1.0 / (1.0 + np.exp(-z))

def tanh_activation(z):
    return np.tanh(z)

def ReLU(z):
   return z * (z > 0)

def draw_activation(f):
    '''
    Draw sigmoid function
    '''
    x = np.linspace(-10.0, 10.0, num=100, endpoint=True)
    plt.figure(1)
    plt.subplot(211)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.plot(x, f(x), 'r-')

def cross_entropy_cost_function(y, y_hat):
    '''
    'y' is the value from the test set
    'y_hat' is the value from the activation function
    '''
    m = y.shape[1]
    cross_entropy_part_0 = np.multiply(y, np.log(y_hat))
    cross_entropy_part_1 = np.multiply((1.0-y), np.log(1.0-y_hat))

    L = -(1./m) * (np.sum(cross_entropy_part_0 + cross_entropy_part_1))
    return L

def prepare_label_array(label_array, number_to_detect):
    '''
    Update training labels and set :
    element ==number_to_detect to 1.0
    element !=number_to_detect to 0.0
    TODO - should be done on the data_loader
    '''
    num_examples = len(label_array)
    label_array_updated = np.copy(label_array)
    index_with_number = np.where(label_array_updated == number_to_detect)[0]
    label_array_updated[:] = 0.0
    label_array_updated[index_with_number] = 1.0
    return label_array_updated.reshape((1, num_examples))

class LogisticRegressionMNIST():
    '''
    Logistic regression to detect a single number
    Aka Neural Network with a single unit
    '''
    def __init__(self, number_to_detect):
        # Value to detect
        self.number_to_detect = number_to_detect

        # Parameters
        self.X = None # training data of shape (num_inputs, num_examples)
        self.b = None # bias of shape (1,1)
        self.w = None # weights of shape (num_inputs, 1)
        self.y = None # output of shape (1, num_examples)
        self.activation_function = None

        # Optimizer Hyperparameters
        self.learning_rate = 0.1
        self.minibatch_size = 1 # Not used
        self.num_epoch = 1000

        # Model Hyperparameters (Unused)
        # Only for future when becomes a fully fonctional neural network
        #self.num_layers = 1
        #self.num_units = 1

    def train(self, training_data_array, training_label_array):
        '''
        Compute the input weights for a single logistic regression
        '''
        # Makes the function predictable
        np.random.seed(0)
        # Prepare training data ('X')
        self.X = training_data_array.transpose()
        # Set the parameters - weights and bias ('w', 'b')
        num_inputs = self.X.shape[0] # len(self.X)
        num_examples = self.X.shape[1]
        self.w = np.random.randn(num_inputs, 1) * 0.01 # random weight to start with
        self.b = np.zeros((1,1))
        # Prepare training labels ('y')
        assert(num_examples == len(training_label_array))
        self.y = prepare_label_array(training_label_array, self.number_to_detect)
        # Set activation function
        self.activation_function = sigmoid_activation

        # Training Loop
        for epoch_id in range(self.num_epoch):
            # Forward propagation to compute the activations with current parameters
            # y_hat = sigma(transpose(w)*X+b)
            z = np.matmul(self.w.T, self.X) + self.b
            y_hat = self.activation_function(z)

            # Compute cost
            cost = cross_entropy_cost_function(self.y, y_hat)

            # update weights
            # TODO - update bias
            dW = (1.0/num_examples) * np.matmul(self.X, (y_hat-self.y).T)

            self.w = self.w - self.learning_rate * dW

            if (epoch_id % 10 == 0):
                print("Epoch", epoch_id, " | cost: ", cost)

    def test(self, test_data_array, test_label_array):
        '''
        Test with test data and the trained neural network
        '''
        # Prepare test data
        X_test = test_data_array.transpose()

        # Test
        z = np.matmul(self.w.T, X_test) + self.b
        y_hat = self.activation_function(z)

        # Map the activations to predictions whether or not its a 'number_to_detect'
        # TODO - DISPLAY confusion_matrix
        predictions = (y_hat>0.5)[0]
        correct_prediction_counter = 0
        for pred_id, pred in enumerate(predictions):
            # Correct prediction
            if (test_label_array[pred_id] == self.number_to_detect)  == pred:
                correct_prediction_counter += 1

        print("Correct Prediction (%) : ", correct_prediction_counter / len(predictions))
