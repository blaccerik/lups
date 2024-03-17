from celery.contrib.abortable import AbortableTask

from model.model_loader import ModelLoader


class PredictTask(AbortableTask):
    abstract = True

    def __init__(self):
        super().__init__()
        self.cpp_model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.cpp_model:
            self.cpp_model = ModelLoader()
        return self.run(*args, **kwargs)