# coding=utf-8
# Created by Meteorix at 2019/7/30
from gevent import monkey; monkey.patch_all()
from flask import Flask, request, jsonify
from service_streamer import ManagedModel, Streamer
from bert_model import Model


app = Flask(__name__)
model = None
streamer = None


class ManagedBertModel(ManagedModel):

    def init_model(self):
        self.model = Model()

    def predict(self, batch):
        return self.model.predict(batch)


@app.route("/naive", methods=["POST"])
def naive_predict():
    inputs = request.form.getlist("s")
    outputs = model.predict(inputs)
    return jsonify(outputs)


@app.route("/stream", methods=["POST"])
def stream_predict():
    inputs = request.form.getlist("s")
    outputs = streamer.predict(inputs)
    return jsonify(outputs)


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    streamer = Streamer(ManagedBertModel, batch_size=64, max_latency=0.1, worker_num=1, cuda_devices=(0, 1, 2, 3))

    from gevent.pywsgi import WSGIServer
    WSGIServer(("0.0.0.0", 5005), app).serve_forever()
