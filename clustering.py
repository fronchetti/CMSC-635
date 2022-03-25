#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'CMSC 635; Group: The Thinker'

import os
from pyksc import ksc
from pyksc import metrics
import numpy
from csv import DictReader
import matplotlib.pyplot as plt

class KSC(object):
    def __init__(self, developers, time_series):
        self.report_file = open('clustering-report.txt', 'w')

        self.developers = developers
        self.time_series = numpy.array(time_series)
        self.clusters_by_time_series = {}
        self.centroids = None
        self.assign = None
        self.best_shift = None
        self.cent_dists = None

    def calculate_beta_cv(self):
        if self.assign is not None:
            return metrics.beta_cv(self.time_series, self.assign)

    def plot_beta_cv(self, min_clusters=2, max_clusters=16):
        k_clusters = [k_i for k_i in range(min_clusters, max_clusters)]
        beta_cv = []

        print('Saving βCV values in "clustering-report.txt" file')
        self.report_file.write('# βCV (for 2 ≤ k ≤ 15):\n')

        for k_i in k_clusters:
            self.get_clusters(k_i)
            beta_cv_i = self.calculate_beta_cv()
            beta_cv.append(beta_cv_i)
            self.report_file.write(str(k_i) + ': ' + str(beta_cv_i) + '\n')

        figure = plt.figure()
        plt.plot(k_clusters, beta_cv, color='black')
        plt.xlabel('# Clusters', fontsize=18)
        plt.ylabel(r'$\beta$cv', fontsize=18)
        plt.title(r'$\beta$cv for 2 $\leq$ k $\leq$ 15')
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        figure.savefig('images/beta_cv.eps', bbox_inches='tight', format='eps', dpi=1000)

    def get_clusters(self, number_of_clusters):
        self.centroids, self.assign, self.best_shift, self.cent_dists = ksc.ksc(self.time_series, number_of_clusters)

        if self.assign is not None:
            for series, cluster in zip(self.time_series , self.assign):
                if cluster in self.clusters_by_time_series.keys():
                    self.clusters_by_time_series[cluster].append(series)
                else:
                    self.clusters_by_time_series[cluster] = [series]

    def plot_clusters(self, k):
        self.get_clusters(k)
        months = None 

        for cluster in self.clusters_by_time_series.keys():
            figure = plt.figure()

            for developer_time_series in self.clusters_by_time_series[cluster]:
                if months is None:
                    months = [-i for i in range(len(developer_time_series) - 1, -1, -1)]

                developer_time_series = [int(i) for i in developer_time_series]

                plt.plot(months, developer_time_series, color='black')

            plt.ylim([0, 475])
            plt.xlim([-75, 3])
            plt.xlabel('Month', fontsize=24)
            plt.ylabel('# Events', fontsize=24)
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)

            filename = 'images/cluster_' + str(cluster) + '.eps'

            if os.path.isfile(filename):
                os.remove(filename)

            figure.savefig(filename, bbox_inches='tight', format='eps', dpi=1000)

    def plot_centroids(self):
        months = None

        print('Saving K-Spectral Centroids (KSC) in "clustering-report.txt" file')
        self.report_file.write('\n# K-Spectral Centroids (KSC):\n')

        for cluster, centroid in zip(range(0, 3), self.centroids):
            growth_rate = centroid[0] + centroid[-1] * 100
            self.report_file.write(str(cluster) + ': ' + str(centroid) + ' (Growth:' + str("{0:.2f}".format(growth_rate)) + ')\n')

            if months is None:
                months = [-i for i in range(len(centroid) - 1, -1, -1)]

            figure = plt.figure()
            plt.plot(months, centroid, color='black')
            # plt.ylim([0, 0.5])
            # plt.xlim([-75, 3])
            plt.xlabel('Month', fontsize=24)
            plt.ylabel('Average', fontsize=24)
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)
            
            filename = 'images/centroid_' + str(cluster) + '.eps'

            if os.path.isfile(filename):
                os.remove(filename)

            figure.savefig(filename, bbox_inches='tight', format='eps', dpi=1000)

if __name__ == '__main__':
    developers_activities_file = open('developers_activities_per_project.csv' , 'r')
    developers_activities = DictReader(developers_activities_file)

    developers = []
    time_series = []

    secondary_columns = ['project_name', 'project_name', 'elite']

    for developer in developers_activities:
        developer_name = developer['developer']
        developer_time_series = [developer[column] for column in developers_activities.fieldnames if column not in secondary_columns]
        developer_time_series = [int(value) for value in developer_time_series]
        developers.append(developer_name)
        time_series.append(developer_time_series)

    k_spectral = KSC(developers, time_series, 'images/')
    k_spectral.plot_beta_cv()
    k_spectral.plot_clusters(3)
    k_spectral.plot_centroids()
