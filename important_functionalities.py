# IMPORTANT FUNCTIONALITIES

### ------- FUNCTIONS -------###
# plot_decision_boundary()
# plot_confusion_matrix()
# plot_custom_model()
# create_tensorboard_callback
# plot_loss_curves()
# load_preprocess()
# walkthrough_directories()
### ------- FUNCTIONS -------###

### imports needed
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import itertools
import graphviz
import datetime as dt
import os

# visualizing model's predictions: 
def plot_decision_boundary(X,y,model):
    '''
    Input: Trained model, Features(X), and labels(y)
    # Creates a meshgrid of different X values
    # make predictions across the meshgrid
    # plot predictions as well as line between different zones where each unique class falls
    '''
    margin=0.1 # margin for meshgrid
    num_points=100 # points in meshgrid
    x_min,x_max=tf.reduce_min(X[:,0]) - margin, tf.reduce_max(X[:,0]) + margin
    y_min,y_max=tf.reduce_min(X[:,1]) - margin, tf.reduce_max(X[:,1]) + margin

    # creating meshgrid
    xx,yy = np.meshgrid(np.linspace(x_min,x_max,num_points),
                        np.linspace(y_min,y_max,num_points))

    # creating X (input) value to make predictions
    x_in = np.c_[xx.ravel(),yy.ravel()] # stack 2D arrays together [(x1,y1),(x2,y2)....]
    
    # making predictions
    y_pred = model.predict(x_in)

    # check for multi-class classification
    if len(y_pred[0]) > 1:
        print("Multi-class classification")
        # we need to reshape our predictions to get them ready for plot
        y_pred=tf.argmax(y_pred,axis=1).numpy().reshape(xx.shape)
    else:
        print("Binary classification")
        y_pred=tf.round(y_pred).numpy().reshape(xx.shape)

    # plotting the decision boundary
    plt.contourf(xx,yy,y_pred,cmap=plt.cm.RdYlBu,alpha=0.7)
    plt.scatter(X[:,0],X[:,1],c=y,s=40,cmap=plt.cm.RdYlBu)
    plt.xlim(x_min,x_max)
    plt.ylim(y_min,y_max)
    plt.show()


# prettifying confusion matrix:

def plot_confusion_matrix(confusion_matrix,figsize = (4,4),classes = None,title_size = 15 ,label_size = 10, text_size = 8):
    # create the confusion matrix
    cm_norm=confusion_matrix.astype("float") / confusion_matrix.sum(axis=1)[:,np.newaxis] # normalize confusion matrix
    n_classes = confusion_matrix.shape[0]

    fig,ax=plt.subplots(figsize=figsize)

    # create a matrix plot
    cax=ax.matshow(confusion_matrix,cmap=plt.cm.Blues) 
    fig.colorbar(cax)

    # Create classes
    if classes:
        labels = classes
    else:
        labels=np.arange(confusion_matrix.shape[0])

    # label the axes
    ax.set(title="Confusion Matrix",
        xlabel="Predicted label",
        ylabel="True label",
        xticks=np.arange(n_classes),
        yticks=np.arange(n_classes),
        xticklabels=labels,
        yticklabels=labels
        )

    # getting the x-axis labels to bottom
    ax.xaxis.set_label_position("bottom")
    ax.xaxis.tick_bottom()

    # adjust label size
    ax.yaxis.label.set_size(label_size)
    ax.xaxis.label.set_size(label_size)

    # adjust title size
    ax.title.set_size(title_size)

    # set the threshold for different colors
    threshold = (confusion_matrix.max() + confusion_matrix.min())/2.0

    # plot the text on each cell 
    for i,j in itertools.product(range(confusion_matrix.shape[0]),range(confusion_matrix.shape[1])):
        plt.text(j,i,f"{confusion_matrix[i,j]}\n({cm_norm[i,j]*100:.2f}%)",
                horizontalalignment = "center",
                verticalalignment = "center",
                color = "white" if confusion_matrix[i,j]>threshold else "black",
                size = text_size)
    
    plt.show()



def plot_custom_model(model, input_shape, show_shapes=True, show_activations=True,          
                      show_trainable_status=True,graph_size="8,8", dpi=100, node_width="1.5", node_height="0.5",ranksep="0.5", nodesep="0.3", title="Model Architecture", save_path=None):
    """
    Plots a detailed visualization of a subclassed Keras model with structured sections
    and different colours for each row while maintaining a single rectangle per layer.

    Parameters:
    - model: The Keras model to visualize.
    - input_shape: The expected input shape (excluding batch size).
    - show_shapes: Whether to display layer shapes.
    - show_activations: Whether to display activation functions.
    - show_trainable_status: Whether to display trainable status.
    - graph_size: The overall size of the graph (e.g., "8,8").
    - dpi: Resolution of the graph (higher = sharper but larger).
    - node_width: Width of each node.
    - node_height: Height of each node.
    - ranksep: Vertical spacing between layers.
    - nodesep: Horizontal spacing between nodes.
    - title: Title displayed at the top of the graph.
    - save_path: If specified, saves the plot as a PNG file.
    """
    dot = graphviz.Digraph(format='png')
    
    # Adjust graph properties
    dot.attr(size=graph_size, dpi=str(dpi), nodesep=nodesep, ranksep=ranksep)
    
    # Add title at the top
    dot.attr(label=f"<<B>{title}</B>>", labelloc="t", fontsize="16", fontcolor="black",fontweight='bold')

    prev_layer = None
    x = tf.keras.layers.Input(shape=input_shape)

    for layer in model.layers:
        layer_name = layer.name
        layer_type = type(layer).__name__

        # Get activation function
        activation_name = model.activations[layer_name]

        # Compute input & output shapes
        try:
            output_shape = layer.compute_output_shape(x.shape) if show_shapes else "N/A"
        except Exception:
            output_shape = "Unknown"

        # checking trainable or not
        if hasattr(layer, "weights") and len(layer.weights) > 0:
            if layer.trainable:
                trainable_status = "Yes"
            else:
                trainable_status = "No"
        else:
            trainable_status = "-"
            

        # Ensure each row exists properly even if not all options are enabled
        act_row = f'<TR><TD COLSPAN="3" BGCOLOR="lightgreen">Activation: {activation_name}</TD></TR>' if show_activations else ""

        shape_row = ""
        if show_shapes:
            shape_row += f'<TD BGCOLOR="lightyellow"><B>Input</B>: {str(x.shape)}</TD>\n'
            shape_row += f'<TD BGCOLOR="lightpink"><B>Output</B>: {output_shape}</TD>'
        else:
            shape_row += '<TD COLSPAN="2"></TD>'  # Maintain table structure

        train_stat_row = f'<TD BGCOLOR="lightgrey"><B>Trainable</B>: {trainable_status}</TD>' if show_trainable_status else ""

        # Ensure at least one row is always present
        if not (show_shapes or show_trainable_status):
            shape_row = '<TD COLSPAN="3"></TD>'

        # Table format with controlled spacing
        label = f"""<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD COLSPAN="3" BGCOLOR="lightblue"><B>{layer_name}</B> ({layer_type})</TD></TR>
            {act_row}
            <TR>
                {shape_row}
                {train_stat_row}
            </TR>
        </TABLE>
        >"""

        # Create the node with adjusted width/height
        dot.node(layer_name, label=label, shape="plaintext", width=node_width, height=node_height)

        # Connect layers sequentially
        if prev_layer:
            dot.edge(prev_layer.name, layer_name)

        prev_layer = layer

    if save_path:
        dot.render(save_path, format="png", cleanup=True)

    return dot


# create tensorboard callback (functionalized because we need to create a new one for each model)

def create_tensorboard_callback(dir_name, experiment_name):
    log_dir = dir_name + "/" + experiment_name + "/" + dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir)
    print(f"Saving TensorBoard log files to : {log_dir}")
    return tensorboard_callback


# plotting validation and training curves separately

def plot_loss_curves(history):
    # loss
    loss=history.history["loss"]
    val_loss=history.history['val_loss']

    # accuracy
    accuracy=tf.multiply(history.history['accuracy'],100)
    val_accuracy=tf.multiply(history.history['val_accuracy'],100)
    
    min_loss=tf.reduce_min(loss)
    min_val_loss=tf.reduce_min(val_loss)
    loc_loss=tf.argmin(loss)+1
    loc_val_loss=tf.argmin(val_loss)+1

    max_accuracy=tf.reduce_max(accuracy)
    max_val_accuracy=tf.reduce_max(val_accuracy)
    loc_acc=tf.argmax(accuracy)+1
    loc_val_acc=tf.argmax(val_accuracy)+1

    epochs = range(1,len(history.history["loss"])+1) # length of one of history object


    # plotting
    plt.figure()
    fig,axs=plt.subplots(1,2,figsize=(8,3))
    
    # loss
    axs[0].plot(epochs,loss,label=f'training loss (min:{min_loss:.2f})')
    axs[0].scatter(loc_loss,min_loss,s=30,color=(1,0,0))
    axs[0].plot(epochs,val_loss,label=f'validation loss (min:{min_val_loss:.2f})')
    axs[0].scatter(loc_val_loss,min_val_loss,s=30,color=(1,0,0))
    axs[0].set_xlabel('Epochs')
    axs[0].set_ylabel('Loss')
    axs[0].set_title('Training & Validation')
    axs[0].legend()

    # accuracy
    axs[1].plot(epochs,accuracy,label=f'training accuracy (max:{max_accuracy:.2f}%)')
    axs[1].scatter(loc_acc,max_accuracy,s=30,color=(0,1,0))
    axs[1].plot(epochs,val_accuracy,label=f'validation accuracy (max:{max_val_accuracy:.2f}%)')
    axs[1].scatter(loc_val_acc,max_val_accuracy,s=30,color=(0,1,0))
    axs[1].set_xlabel('Epochs')
    axs[1].set_ylabel('Loss/Accuracy')
    axs[1].set_title('Training & Validation')
    axs[1].legend()

    plt.tight_layout()
    plt.show()

# load and pre-process image
def load_preprocess(filename,shape=(224,224,3)):
    # load the image
    img=tf.io.read_file(filename=filename)
    img=tf.image.decode_image(img)
    
    # resize
    img=tf.image.resize(img,shape[:2])
    # rescale/normalize image
    img=img/255.0
    return img


# walkthrough directories
def walkthrough_directories(dir_name:str):
    '''
    Walks through directories and prints the number of directories and files in each directory
    '''
    for dirpath,dirnames,filenames in os.walk(dir_name):
        print(f"There are {len(dirnames)} directories and {len(filenames)} images in {dirpath}")