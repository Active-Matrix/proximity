import torch
import torch.nn as nn
from transformers import DistilBertTokenizer, DistilBertModel
from torchtune.modules import RotaryPositionalEmbeddings

def load_BERT():
    """
    Load the BERT model and tokenizer.
    """
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    model = DistilBertModel.from_pretrained("distilbert-base-uncased")
    print("BERT Model and tokenizer loaded successfully.")
    return tokenizer, model

# Function to get sentence embedding
def get_embedding(text) -> torch.Tensor:

    if len(text) == 0:
        raise ValueError("Input list/str cannot be empty.")
    
    try:
        # Load BERT model and tokenizer
        tokenizer, model = load_BERT()

    except Exception as e:
        # Handle the error if the model fails to load
        print(f"Error loading BERT model: {e}")
        return  

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128)
    
    with torch.no_grad():
        outputs = model(**inputs)
        cls_embedding = outputs.last_hidden_state[:, 0, :]  # CLS token embedding
    
    return cls_embedding


class LSTMEmbeddingGenerator(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim, dropout=0.1):
        """
        LSTM model for generating embeddings from position-encoded input.

        Args:
            input_dim (int): head_dim * num_heads (flattened input dimension)
            hidden_dim (int): Number of hidden units in LSTM.
            num_layers (int): Number of LSTM layers.
            output_dim (int): Final embedding size.
            dropout (float): Dropout rate (default 0.1).
        """
        super(LSTMEmbeddingGenerator, self).__init__()

        # LSTM layer
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=dropout)

        # Fully connected layer to generate the final embedding
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        """
        Forward pass of the LSTM embedding model.

        Args:
            x (torch.Tensor): Input of shape (batch_size, timesteps, head_dim, num_heads)

        Returns:
            torch.Tensor: Output embedding of shape (batch_size, output_dim)
        """
        batch_size, timesteps, _, _ = x.shape

        # Flatten last two dimensions (head_dim * num_heads)
        x = x.view(batch_size, timesteps, -1)

        # Pass through LSTM
        _, (hn, _) = self.lstm(x)  # hn is (num_layers, batch, hidden_dim)

        # Take the last hidden state of the last LSTM layer
        # last_hidden_state = hn[-1]  # Shape: (batch_size, hidden_dim)

        # Project to embedding space
        embedding = self.fc(hn[-1])  # Shape: (batch_size, output_dim)

        return embedding


class recommendationModel(nn.Module):
    def __init__(self, batch, timesteps, head_dim, num_heads, hidden_dim, num_layers, output_dim, dropout=0.1):
        """
        Initializes the recommendationModel with the given parameters.

        Args:
            batch (int): The batch size for training.
            timesteps (int): The number of timesteps for the input sequence.
            head_dim (int): The dimension of each attention head.
            num_heads (int): The number of attention heads.
            hidden_dim (int): The hidden dimension for the LSTM embedding generator.
            num_layers (int): The number of layers for the LSTM embedding generator.
            output_dim (int): The output dimension for the LSTM embedding generator.
            dropout (float, optional): The dropout rate. Default is 0.1.
        """

        super(recommendationModel, self).__init__()

        self.batch = batch
        self.timesteps = timesteps
        self.num_heads = num_heads
        self.head_dim = head_dim

        self.rope = RotaryPositionalEmbeddings(head_dim)
        self.LSTM_embedding = LSTMEmbeddingGenerator(input_dim=head_dim * num_heads,
                               hidden_dim=hidden_dim,
                               num_layers=num_layers,
                               output_dim=output_dim,
                               dropout=dropout)

    def forward(self, x):
        
        x = get_embedding(x)

        x = x.view(self.batch, self.timesteps, self.num_heads, self.head_dim)

        x = self.rope(x)
        x = self.LSTM_embedding(x)

        return x