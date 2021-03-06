
from InputData.config import *
from Evaluation import generateRandomData as gd
import Backend.RecommendationService.ClusteringService.clustering as cl
import DatabaseIO.readDatabase as reda
import Frontend.DataViewer.plotclustering as pclust
from sklearn.metrics.cluster import adjusted_rand_score
import pandas as pd
import matplotlib.pyplot as plt
import os


def plotevaluation(seed, samples, features, centers, std, randomNumberOfVotes, silent = False, showplot = True):
    if not silent:  print("+ plotevaluation")

    #### All values seperately
    data = pd.read_csv('Evaluation/eval/results.csv', sep=",", header=None)
    #Iter, Score, Votes
    data.columns = ["Iter", "Score", "Votes"]
#    if not silent:  print(data)

    #### Grouped
    dataGrouped = data.groupby('Votes').mean()
    dataGrouped['Votes'] = dataGrouped.index
#    if not silent:  print(dataGrouped)

    plt.clf()

    myfig, ax = plt.subplots(1, 2, constrained_layout=True, figsize=(10, 10),sharex=True)
    suptitle = ' Score vs. Votes: ' + str(samples) + " " + str(features) + " " + str(centers) + " " + str(std) + " " + str(evalIterations) + " " + str(seed)
    myfig.suptitle(t = suptitle, y = 0.97)

    ax[0].scatter(data['Votes'], data['Score'])
    ax[0].set_title('Singular Values')
    ax[1].plot(dataGrouped['Votes'], dataGrouped['Score'])
    ax[1].set_title('Average Values')

    for axi in ax.flat:
        axi.set(xlabel='Votes', ylabel='Score')
    for axi in ax.flat:
        axi.label_outer()

    filename = "Evaluation/eval/Evaluation" + suptitle + ".pdf"
    print(filename)
    myfig.savefig(filename)
    if showplot:    myfig.show()

    if not silent:  print("- plotevaluation")


def saveOutputFromRun(silent = True):
    if not silent:  print("+ saveOutputFromRun")
    if not silent:  print("- saveOutputFromRun")


def calculateResultScore(silent = True):
    if not silent:  print("+ calculateResultScore")

    (X1, y1) = reda.readTransformedData()
    (X2, y2, z) = reda.readClusteredData()

    y1 = y1.to_numpy().flatten()

    score = adjusted_rand_score(y1, y2)

    if not silent:  print("- calculateResultScore")

    return score


def doEvaluate(silent = True, showplot = False):
    if not silent:  print("+ doEvaluate")

#    global seed
#    print(seed)
#    allocateRandomVariables()
#    seed = seed * 2
    (df, seed, samples, features, centers, std, MaxNumberOfVotes) = gd.generate_Data()
#    print(seed)

    # special case: Without feedback learning:
    UsedFeedback[-1] = []
    gd.importData()
    cl.doClustering(initial=True, numClusters = centers)
    if showplot: pclust.plotClustering(Inputdata="Realdata", output="here", currentIteration=-2)
    if saveLocalPlotsForEachIteration:
        if showplot: pclust.plotClustering(Inputdata="Clustereddata", output="here", currentIteration=-1)
    else:
#        pclust.plotClustering(Inputdata="Realdata")
        if showplot: pclust.plotClustering(Inputdata="Clustereddata")
    Scores[-1] = calculateResultScore()
    evalIter = -1
    NumberOfVotes[evalIter] = 0
    outputline = "Iteration: "+str(evalIter)+" Score: "+str(Scores[evalIter])+" Votes: "+str(NumberOfVotes[evalIter])+" "+str(UsedFeedback[evalIter])+'\n'
    if not silent:  print(outputline)
    with open('Evaluation/eval/results.txt', 'a') as the_file:
        the_file.write(outputline)
    if os.path.exists("Evaluation/eval/results.csv"):
        os.remove("Evaluation/eval/results.csv")
    #Iter, Score, Votes
    outputline = str(evalIter)+","+str(Scores[evalIter])+","+str(NumberOfVotes[evalIter])+'\n'
    with open('Evaluation/eval/results.csv', 'a') as the_file:
        the_file.write(outputline)

    # now iterate and create different feedbacks:
    for evalIter in range(evalIterations):
        if not silent:  print("Starting iteration:", evalIter)

        if not silent:  print("Deleting previous feedback.")
        gd.delete_feedback()
        used_combinations = []

#        rand.seed(seed)
        randomNumberOfVotes = rand.randint(1, MaxNumberOfVotes)
#        randomNumberOfVotes = rand.randint(1, 399)
        NumberOfVotes[evalIter] = randomNumberOfVotes
        #if not silent:
        if not silent:  print("In this iteration we have", randomNumberOfVotes, "votes.")
        for i in range(randomNumberOfVotes):
            if not silent:  print("Generating vote number:", i)

            # create random vote and insert into table
            inserted = False
            tries = 0 # needed to make sure that we wont do infinte loops here (in case that all constelation for randomNumberOfVotes have been inserted already)
            while inserted == False and tries < 1000:
                tries += 1
                # randomPoint1 shall be smaller than randomPoint2
                randomPoint1 = rand.randint(0,samples-1)
                randomPoint2 = rand.randint(0,samples-1)
                if randomPoint2 < randomPoint1:
                    randomPointtmp = randomPoint1
                    randomPoint1 = randomPoint2
                    randomPoint2 = randomPointtmp
                if not randomPoint1 == randomPoint2:
                    if not tuple((randomPoint1,randomPoint2)) in used_combinations:
                        # insert
                        gd.write_specific_feedback(df, randomPoint1, randomPoint2)
                        if not silent:  print(tuple((randomPoint1,randomPoint2)), "not in used combinations; writing to table")
                        used_combinations.append(tuple((randomPoint1, randomPoint2)))
                        inserted = True
                    else:
                        # do not insert
                        if not silent:  print(tuple((randomPoint1,randomPoint2)), "in used combinations")
                        inserted = False
            if not silent:  print("Vote number:", i,"generated.")
        UsedFeedback[evalIter] = used_combinations

        if not silent:  print("Importing Data")
        gd.importData()

        if not silent:  print("Starting Learning and Clustering")
        cl.doClustering(initial = False, numClusters = centers)

        if not silent:  print("Plotting Clusters")
        if saveLocalPlotsForEachIteration:
            if showplot: pclust.plotClustering(Inputdata="Clustereddata", output="here", currentIteration = evalIter)
        else:
            if showplot: pclust.plotClustering(Inputdata="Clustereddata")
        if not silent:  print("Starting Evaluation")
        Scores[evalIter] = calculateResultScore()
        outputline = "Iteration: "+str(evalIter)+" Score: "+str(Scores[evalIter])+" Votes: "+str(NumberOfVotes[evalIter])+" "+str(UsedFeedback[evalIter])+'\n'
        if not silent:  print(outputline)
        with open('Evaluation/eval/results.txt', 'a') as the_file:
            the_file.write(outputline)
        #Iter, Score, Votes
        outputline = str(evalIter)+","+str(Scores[evalIter])+","+str(NumberOfVotes[evalIter])+'\n'
        with open('Evaluation/eval/results.csv', 'a') as the_file:
            the_file.write(outputline)
#    print(NumberOfVotes, UsedFeedback, Scores)
    with open('Evaluation/eval/results.txt', 'a') as the_file:
        the_file.write('\n')
    plotevaluation(seed, samples, features, centers, std, randomNumberOfVotes)
    if not silent:  print("- doEvaluate")


def doEvaluateLoop(repeats):
    for rep in range(repeats):
        print("Loop:", rep)
        doEvaluate()


doEvaluateLoop(1)

