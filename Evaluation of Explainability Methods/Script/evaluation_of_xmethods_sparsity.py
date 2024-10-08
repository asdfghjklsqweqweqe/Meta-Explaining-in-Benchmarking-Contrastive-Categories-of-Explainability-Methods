# -*- coding: utf-8 -*-
"""Evaluation_of_XMethods_SPARSITY.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16TFXt02eaEyBHOlqE9pP-TfNRJAMkPnT
"""

import torch
import statistics
from statistics import mean
import csv
from sklearn import metrics
from copy import deepcopy

class evalaution_of_xmethods_sparsity(object):
    def __init__(self, a_trained_model, test_data):
        super(evalaution_of_xmethods_sparsity, self).__init__()
        self.a_trained_model = a_trained_model
        self.test_data = test_data


    def is_salient(self, score, importance_threshold):
        if importance_threshold == score == 0:
            return True
        if importance_threshold == score == 1:
            return False
        if importance_threshold < score:
            return True
        else:
            return False

    def normalize_saliency(self, input_graphs, sal_maps):
        Graphs_new_gradients = []
        for graph_grads in sal_maps:
            new_gradients = []
            for node_grads in graph_grads:
                val = (node_grads-min(graph_grads))/(max(graph_grads)-min(graph_grads)) if (max(graph_grads)-min(graph_grads)) != 0 else 0
                new_gradients.append(val)
            Graphs_new_gradients.append(new_gradients)

        return Graphs_new_gradients

    def binarize_nodes(self, your_dataset, saliency_maps, importance_threshold):
        attribution_scores_class0 = self.normalize_saliency(your_dataset, saliency_maps)

        class_0_salient_nodes = []
        class_0_binarized = []
        for i in range(len(attribution_scores_class0)):
            sample_graph = deepcopy(your_dataset[i])
            class_0_graph = []
            for j in range(len(attribution_scores_class0[i])):
                if self.is_salient(attribution_scores_class0[i][j], importance_threshold):
                    class_0_graph.append(1)
                else:
                    class_0_graph.append(0)
            class_0_binarized.append(class_0_graph)


        return class_0_binarized

    def count_important_nodes(self, salient_list):
        return sum(salient_list)

    def my_sparsity(self, your_dataset, saliencies_for_multiple_classes, importance_threshold):
        try:
            saliency_maps_binarized = {}
            for key, value in saliencies_for_multiple_classes.items():
                salient_nodes = self.binarize_nodes(your_dataset, value, importance_threshold)
                saliency_maps_binarized[key] = salient_nodes


            sparsity_list = []
            for i in range(len(saliencies_for_multiple_classes[0])):
                d= sum([self.count_important_nodes(saliency_maps_binarized[j][i]) for j in range(len(saliencies_for_multiple_classes.keys()))])
                d = d / (len(saliencies_for_multiple_classes[0][i]) * len(saliencies_for_multiple_classes.keys()))
                sparsity_list.append(1 - d)

            return mean(sparsity_list)
        except:
            print("attributions are not in appropriate shape")