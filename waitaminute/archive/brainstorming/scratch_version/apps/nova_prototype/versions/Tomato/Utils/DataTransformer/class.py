from DataTransformer.transformers import transformers as tr

class DataTransformer:
    # This class is used to transform data from one format to another
    # It is used for debugging and testing purposes, but could someday be used in production
    # It's a beast of a class, but it's a good example of how to use classes to transform data
    def __init__(self):
      for item in tr.__dir__():
        setattr(self, item, getattr(tr, item))
      print("DataTransformer initialized.")
      print("Installed transformers:")
      for item in self.__dir__():
        print(item)

    def return_data(self):
        return self.data


    def add_custom_transform(self, name, transform_func):
        setattr(self, name, transform_func)
        self.custom_transforms[name] = transform_func

    def run_custom_transform(self, name, data):
        if name not in self.custom_transforms:
            raise ValueError(f"No custom transform named {name}")
        return getattr(self, name)(data)