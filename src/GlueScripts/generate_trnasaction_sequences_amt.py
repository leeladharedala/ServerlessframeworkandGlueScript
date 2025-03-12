import sys
import random
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType
from faker import Faker
from awsglue.utils import getResolvedOptions

spark = SparkSession.builder \
    .appName("GenerateTransactionSequences") \
    .config("spark.sql.parquet.compression.codec", "snappy") \
    .getOrCreate()

fake = Faker()

args = getResolvedOptions(sys.argv, ['S3_BUCKET'])


s3_bucket = f"s3://{args['S3_BUCKET']}"


transactions_path = "FakeUserData/Transactions"
sequences_amt_path = "FakeUserData/TransactionSequencesAmt"

TRANSACTIONS_PER_ID = (1, 7)  

df_transactions = spark.read.parquet(f"{s3_bucket}/{transactions_path}")

rdd_transactions = df_transactions.rdd

    
def generate_sequences(row):
        transaction_id, user_id, total_amount, date, description = row
        num_sub_transactions = random.randint(*TRANSACTIONS_PER_ID)

        # Define cyclic sequence pattern
        seq_num_pattern = [1, 3, 5, 7]
        selected_seq_nums = [seq_num_pattern[i % 4] for i in range(num_sub_transactions)]

        # Generate random fractions summing up to 1
        fractions = [random.uniform(0.1, 1) for _ in range(num_sub_transactions)]
        total_fraction = sum(fractions)
        normalized_fractions = [f / total_fraction for f in fractions]

        return [
            (
                f"{transaction_id}-{i}", 
                i, 
                selected_seq_nums[i],  
                transaction_id,
                user_id,
                round(total_amount * normalized_fractions[i], 2),  
                date,
                fake.sentence(nb_words=6)
            )
            for i in range(num_sub_transactions)
        ]

   
rdd_sequences = rdd_transactions.flatMap(generate_sequences)

   
sequence_schema = StructType([
        StructField("sequence_id", StringType(), False),
        StructField("sortkey", IntegerType(), False),
        StructField("sequence_num", IntegerType(), False),  
        StructField("transaction_id", StringType(), False),
        StructField("user_id", StringType(), False),
        StructField("transaction_amount", FloatType(), False),
        StructField("transaction_date", StringType(), False),
        StructField("description", StringType(), False),
    ])
    
df_sequences = spark.createDataFrame(rdd_sequences, schema=sequence_schema)
    
df_sequences = df_sequences.orderBy("transaction_id", "sortkey")
    
df_sequences = df_sequences.drop("sortkey")

    
df_sequences.write.mode("overwrite").parquet(f"{s3_bucket}/{sequences_amt_path}")
print(f"Transaction sequences written successfully to S3: {s3_bucket}/{sequences_amt_path}")

spark.stop()