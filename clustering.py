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
        self.time_series_by_cluster = {}
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
        figure.savefig('images/beta_cv.png', bbox_inches='tight', format='png', dpi=1000)

    def get_clusters(self, number_of_clusters):
        self.centroids, self.assign, self.best_shift, self.cent_dists = ksc.ksc(self.time_series, number_of_clusters)

        if self.assign is not None:
            for developer, series, cluster in zip(self.developers, self.time_series , self.assign):
                if cluster in self.time_series_by_cluster.keys():
                    self.time_series_by_cluster[cluster].append([developer, series])
                else:
                    self.time_series_by_cluster[cluster] = [[developer, series]]

    def plot_clusters(self, k):
        self.get_clusters(k)
        months = None 

        for cluster in self.time_series_by_cluster.keys():
            figure = plt.figure()
            elite = 0
            nonelite = 0
            elite_avg = 0
            nonelite_avg = 0
            max_elite = [None, 0]
            min_elite = [None, 99999]
            max_nonelite = [None, 0]
            min_nonelite = [None, 99999]

            for developer in self.time_series_by_cluster[cluster]:
                if months is None:
                    months = [-i for i in range(len(developer[1]) - 1, -1, -1)]

                developer_time_series = [0.0001 if value == '0' else int(value) for value in developer[1]]
                total_events_by_developer = sum(developer_time_series)

                if (developer[0][2] == 'TRUE'):
                    elite_avg += total_events_by_developer

                    if total_events_by_developer >= max_elite[1]:
                        max_elite = [developer[0][0], total_events_by_developer]

                    if total_events_by_developer <= min_elite[1]:
                        min_elite = [developer[0][0], total_events_by_developer]

                    elite += 1
                    plt.plot(months, developer_time_series, color='green')
                else:
                    nonelite_avg += total_events_by_developer

                    if total_events_by_developer >= max_nonelite[1]:
                        max_nonelite = [developer[0][0], total_events_by_developer]

                    if total_events_by_developer <= min_nonelite[1]:
                        min_nonelite = [developer[0][0], total_events_by_developer]

                    nonelite += 1
                    plt.plot(months, developer_time_series, color='red')

            print('Cluster: ' + str(cluster))
            elite_avg = elite_avg / elite
            nonelite_avg = nonelite_avg / nonelite
            print('Average: Elite:' + str(elite_avg) + ' Nonelite: ' + str(nonelite_avg))
            print('Elite: ' + str(elite) + ' Nonelite: ' + str(nonelite) + '\n')
            print('Elite Max:' + str(max_elite) + ' Min: ' + str(min_elite))
            print('Non elite Max: ' + str(max_nonelite) + ' Min: ' + str(min_nonelite))
            print('\n\n\n')

            plt.ylim([0, 1500])
            plt.xlim([-46, 1])
            plt.xlabel('Months', fontsize = 16, fontweight = 'bold')
            plt.ylabel('# Events', fontsize = 16, fontweight = 'bold')
            plt.xticks(fontsize = 14)
            plt.yticks(fontsize = 14)

            filename = 'images/cluster_' + str(cluster) + '.png'

            if os.path.isfile(filename):
                os.remove(filename)

            figure.savefig(filename, bbox_inches='tight', format='png', dpi=1000)

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
            plt.ylim([0, 1.0])
            plt.xlim([-46, 1])
            plt.xlabel('Months', fontsize=16)
            plt.ylabel('Average', fontsize=16)
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            
            filename = 'images/centroid_' + str(cluster) + '.png'

            if os.path.isfile(filename):
                os.remove(filename)

            figure.savefig(filename, bbox_inches='tight', format='png', dpi=1000)

if __name__ == '__main__':
    developers_activities_file = open('developer_activities_per_project.csv' , 'r')
    developers_activities = DictReader(developers_activities_file)

    developers = []
    time_series = []

    info_columns = ['developer', 'project', 'elite']
    bots = ['tensorflow-copybara'] # Ignore bots

    for developer in developers_activities:
        if developer['developer'] not in bots:
            developer_info = [developer[information] for information in info_columns]
            developer_time_series = [developer[column] for column in developers_activities.fieldnames if column not in info_columns]
            developer_time_series = [0.0001 if value == '0' else int(value) for value in developer_time_series]
            developers.append(developer_info)
            time_series.append(developer_time_series)

    k_spectral = KSC(developers, time_series)
    # k_spectral.plot_beta_cv()
    k_spectral.plot_clusters(3)
    k_spectral.plot_centroids()
