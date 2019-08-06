#!/usr/bin/python
# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import tensorflow as tf
import os

""" 
usage: 
Processes all .jpg, .png, .bmp and .gif files found in the specified directory and its subdirectories.
 --PATH ( Path to directory of images or path to directory with subdirectory of images). e.g Path/To/Directory/
 --Model_PATH path to the tensorflow model
"""
def ensure_directory(file_path):
    """Checks the given file path for a directory, and creates one if not already present.

    Args:
        file_path: a string representing a valid URL
    """

    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def predict(image_directory, project_data):

    model_path = "savedmodel/"

    crystal_images = []
    for file in os.listdir(image_directory):
        if os.path.isfile(image_directory + "/" + file):
            crystal_images.append(image_directory + "/" + file)
    size = len(crystal_images)


    def load_images(file_list):
        for i in file_list:
            file = open(i, "rb")
            yield {"image_bytes": [file.read()]}, i


    iterator = load_images(crystal_images)

    predicter = tf.contrib.predictor.from_saved_model(model_path)

    k = 0
    for _ in range(size):
        data, name = next(iterator)
        results = predicter(data)

        vals = results['scores'][0]
        vals = vals * 100
        vals = [vals[0], vals[1], vals[2], vals[3]]
        index = vals.index(max(vals))
        notes_path = os.path.join(os.pardir, os.pardir, "Image_Data/" + project_data[0] + "/")
        ensure_directory(notes_path)
        notes_path = notes_path + project_data[1] + "/"
        ensure_directory(notes_path)
        notes_path = notes_path + project_data[2] + "/"
        ensure_directory(notes_path)
        notes_path = notes_path + str(project_data[3]) + "/"
        ensure_directory(notes_path)
        notes_path = name.replace("Images", "Image_Data")
        notes_path = notes_path.replace(".jpg", "")
        ensure_directory(notes_path + "/")

        data_file = open(notes_path + "/" + "image_data_0.txt", "w")
        classification = ""
        if index == 0:
            classification = "Crystal"
        elif index == 1:
            classification = "Other"
        elif index == 2:
            classification = "Precipitate"
        elif index == 3:
            classification = "Clear"

        data_file.write("Project Code:" + project_data[0] + ':\n')
        data_file.write("Target Name:" + project_data[1] + ':\n')
        data_file.write("Plate Name:" + project_data[2] + ':\n')
        data_file.write("Date:" + str(project_data[3]) + ':\n')
        data_file.write('\n')

        data_file.write("Classification:" + classification + ':\n')
        data_file.write('\n')
        data_file.write('\n')
        data_file.write("Notes:" + '\n')
        data_file.write('\n')
        data_file.close()

        #print('Image path: ' + name, 'Crystal: ' + str(vals[0]), 'Other: ' + str(vals[1]),
        #          'Precipitate: ' + str(vals[2]), 'Clear ' + str(vals[3]))
