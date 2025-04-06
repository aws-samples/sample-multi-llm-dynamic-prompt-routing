# Generating FAISS reference index for [Semantic Routing](../semantic-router/README.md)

To implement the routing layer in semantic routing, you first need to create a reference set of prompts that represents the full spectrum of diverse tasks your application needs to handle. This set serves as the foundation for the semantic matching process, enabling the application to correctly categorize incoming queries. 

As an illustrative example for our education tutor chatbot, below we've provided a sample catalog with five questions for each of the history and math topics. In a real-world implementation, you would likely need a much larger and more diverse set of reference questions to ensure robust routing performance.

History:
1. What were the main causes of World War I?
2. What region of the United States saw the largest economic growth as a result of the Industrial Revolution?
3. Who was the first man on the moon?
4. What country gifted the United States with the Statue of Liberty?
5. What major event sparked the beginning of the Great Depression in 1929?

Math:
1. Solve the quadratic equation: 2x^2 + 5x - 12 = 0
2. Find the derivative of f(x) = 3x^4 - 2x^3 + 5x - 7
3. In a right triangle, if one angle is 30° and the hypotenuse is 10 cm, find the lengths of the other two sides.
4. Determine the area of the region bounded by y = x^2, y = 4, and the y-axis.
5. If log_2(x) + log_2(y) = 5 and xy = 64, find the values of x and y.

## Generation of the reference index in [FAISS](https://github.com/facebookresearch/faiss)
In this repo, we will leverage Amazon Titan Text Embeddings model to convert all questions in the reference set into embeddings. These embeddings will then be saved as a FAISS index. Additionally, the corresponding topic for each question (e.g., history or math) will be saved as metadata, which will serve as a reference label set.

To generate the FAISS reference index and the reference label set for the above catalog, follow these steps:

1. Ensure you have Python 3.9 installed on your system.

2. Create and activate a virtual Python environment.

```
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the required libraries:

```
python3 -m pip install -r requirements.txt
```

3. Set up your AWS credentials for Amazon Bedrock access. You can do this by configuring the AWS CLI or setting environment variables.

5. Run the provide Python script using the following command:

```
python3 generate_faiss_reference_index.py
```

This will create two files in your current directory:
- `reference_index.faiss`: The FAISS index file
- `reference_labels.json`: A JSON file containing the corresponding labels

You need to copy these two files inside the semantic-routing/faiss_layer/ folder before deplying the Semantic Routing solution.
