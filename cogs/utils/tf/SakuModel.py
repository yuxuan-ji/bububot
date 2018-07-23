import tensorflow as tf


class SakuModel:

    def __init__(self, labels_path, graph_path):
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile(labels_path)]
        with tf.gfile.FastGFile(graph_path, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')

    def predict(self, image_data):
        with tf.Session() as sess:

            # Feed the image_data as input to the graph and get first prediction
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
            
            predictions = sess.run(softmax_tensor,
                     {'DecodeJpeg/contents:0': image_data})
            
            # Sort to show labels of first prediction in order of confidence
            top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
            
            for node_id in top_k:
                human_string = self.label_lines[node_id]
                score = predictions[0][node_id]
                score_percent = score * 100
                return 'I am {:.5f}% sure that this is {}'.format(score_percent, human_string.title())
