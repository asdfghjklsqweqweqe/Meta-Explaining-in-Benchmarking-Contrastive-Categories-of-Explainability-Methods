# -*- coding: utf-8 -*-
"""Evaluation_of_XMethods_Contrastivity.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SDsxtVK9OXf8YAI3qXpPn1O0r4tvlPdH
"""

import torch
import math
import statistics
from statistics import mean
import csv
import itertools
from sklearn import metrics
from copy import deepcopy

class evalaution_of_xmethods_contrastivity(object):
    def __init__(self, a_trained_model, test_data):
        super(evalaution_of_xmethods_contrastivity, self).__init__()
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

    def standardize_for_contrastivity(self, sal_maps, contrast_coeff):
        final = []
        for i, graph in enumerate(sal_maps):
            temp = []
            for node in graph:
                if math.isnan(node):
                    temp.append(0)
                    # print("sal map: ", i, node)
                # if math.isnan(node*contrast_coeff):
                #     print("multiplication is Nan")
                elif node != 1.0:
                    temp.append(node*contrast_coeff - int(node*contrast_coeff))
                else:
                    temp.append(node)
            final.append(temp)
        return final

    def normalize_saliency(self, input_graphs, sal_maps):
        Graphs_new_gradients = []
        for graph_grads in sal_maps:
            new_gradients = []
            for node_grads in graph_grads:
                val = (node_grads-min(graph_grads))/(max(graph_grads)-min(graph_grads)) if (max(graph_grads)-min(graph_grads)) != 0 else 0
                new_gradients.append(val)
            Graphs_new_gradients.append(new_gradients)

        return Graphs_new_gradients

    def binarize_scores(self, your_dataset, saliency_maps, importance_threshold, contrast_coeff):
        attribution_scores = self.standardize_for_contrastivity(saliency_maps, contrast_coeff)
        attribution_scores = self.normalize_saliency(your_dataset, attribution_scores)

        binarized_attribution_scores_list = []
        for i in range(len(attribution_scores)):
            binary_score = ''
            sample_graph = deepcopy(your_dataset[i])
            for j in range(len(attribution_scores[i])):
                if self.is_salient(attribution_scores[i][j], importance_threshold):
                    binary_score += '1'
                else:
                    binary_score += '0'
            binarized_attribution_scores_list.append(binary_score)
        return binarized_attribution_scores_list

    def hamming_distance(self, string1, string2):

        distance = 0
        L = len(string1)
        for i in range(L):
            if string1[i] != string2[i]:
                distance += 1
        return distance

    def my_contrastivity(self, your_dataset, saliencies_for_multiple_classes, importance_threshold, contrast_coeff):
        # try:
            key_combinations = list(itertools.combinations(saliencies_for_multiple_classes.keys(), 2))
            contrastivity_combinations = []
            for (key1, key2) in key_combinations:
                binarized_salient_nodes_for_key1 = self.binarize_scores(your_dataset, saliencies_for_multiple_classes[key1], importance_threshold, contrast_coeff)
                binarized_salient_nodes_for_key2 = self.binarize_scores(your_dataset, saliencies_for_multiple_classes[key2], importance_threshold, contrast_coeff)
                result_list = []
                for class_0, class_1 in zip(binarized_salient_nodes_for_key1, binarized_salient_nodes_for_key2):
                    d = self.hamming_distance(class_0, class_1) / len(class_0)
                    result_list.append(d)
                contrastivity_combinations.append(mean(result_list))
            return mean(contrastivity_combinations)
        # except:
        #     print("attributions are not in appropriate shape")

#contrastivity_xmethod_example = eval_xai_contrastivity.evalaution_of_xmethods_contrastivity(model_name="GCN_plus_GAP", a_trained_model=GNN_Model#,
#                                                                     test_data=test_dataset, norm_coeff=1)
#contrastivity_score = contrastivity_xmethod_example.my_contrastivity(test_dataset, importance_levels_for_feature_of_nodes_zero, 
#                                                                     importance_levels_for_feature_of_nodes_one, importance_threshold=0.5,
#                                                                     contrast_coeff=1e+9)
#print("Contrastivity_Score: ", contrastivity_score)