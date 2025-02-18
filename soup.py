from pymilvus import MilvusClient, DataType, Function, FunctionType

client = MilvusClient(uri="https://in03-6d0166da8e21ddd.serverless.gcp-us-west1.cloud.zilliz.com",
                      token="ac9e06ae092afb90f90b61de112607cb2918fbba386dfc45edba79c7a39639ef9c3abdfd45b2522d7699c5b12e7e6c8638fcc794")

# schema = client.create_schema()

# schema.add_field("ID", datatype=DataType.INT64, is_primary=True, auto_id=True)
# schema.add_field("text", datatype=DataType.VARCHAR, max_length=2000, enable_analyzer=True)
# schema.add_field("vector", datatype=DataType.FLOAT_VECTOR, dim=768)
# schema.add_field(field_name="sparse", datatype=DataType.SPARSE_FLOAT_VECTOR)

# bm25_function = Function(
#     name="text_bm25_emb",
#     input_field_names=["text"],
#     output_field_names=["sparse"]
#     function_type=FunctionType.BM25,
# )

# schema.add_function(bm25_function)

# index_params = client.prepare_index_params()

# index_params.add_index(
#     field_name="sparse",
#     index_type="AUTOINDEX",
#     metric_type="BM25"
# )

# index_params.add_index(
#     field_name="vector",
#     index_type="IVF_FLAT",
#     metric_type="COSINE"
# )

# client.drop_collection("Capstonev2")  # Deletes the existing collection
# client.create_collection(collection_name="Capstonev2", schema=schema, index_params=index_params)

# search_params = {
#     "nprobe": 16
# }

# hi = client.search(
#     collection_name='Capstonev2', 
#     data=['B.1'],
#     anns_field='sparse',
#     output_fields=['ID', 'text'],
#     search_params=search_params
# )

# print(hi)

client.drop_collection("Capstone")  # Deletes the existing collection