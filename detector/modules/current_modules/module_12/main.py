import joblib
import networkx as nx
import json
import r2pipe, os, sys
import numpy as np
from param_parser import parameter_parser
import joblib as jb
import pathlib

inValid=0
def create_graph(path):
    r2 = r2pipe.open(path)
    r2.cmd('aaa')
    r2.cmd('agCd')
    data = r2.cmd('agCd')
    label={}
    G=nx.DiGraph()
    for lines in data.split('\n'):
        tmp=[]
        for words in lines.split():
            if words[0]=='"':
                words=words.replace('"','')
            tmp.append(words)    
        try:
            if tmp[1][1]=='l':
                func=tmp[1][7:]
                func=func.replace('"','')
                label[tmp[0]]=func
        except:
            pass
       
    for lines in data.split('\n'):
        tmp=[]
        for words in lines.split():
            if words[0]=='"':
                words=words.replace('"','')
            tmp.append(words)
        try:
            if tmp[1]=='->':
                G.add_edge(label[tmp[0]],label[tmp[2]])
        except:
            pass
    return G

def get_density(G):
    global inValid
    degree = {d[0]:d[1] for d in G.degree(G.nodes())}
    if len(degree)==0:
      inValid=1
    elif len(degree)==1:
      inValid=1
    else:
      inValid=0
    if inValid==0:
      density = (sum(degree.values())/(len(degree)-1)) / len(degree)
    else:
      density=-1


    return density

def shortest_path(G):

    # shortest_path=dict(nx.all_pairs_shortest_path(G.to_undirected()))
    # shortest_path_length={}

    # for start in shortest_path:
    #     tmp={}
    #     for target in shortest_path[start]:
    #         if start!=target:
    #             tmp[target]=len(shortest_path[start][target])
    #     shortest_path_length[start]=tmp

    List=[]
    for C in (G.subgraph(c).copy() for c in nx.connected_components(G.to_undirected())):
        List.append(nx.average_shortest_path_length(C))
    shortest_path=[]
    shortest_path.append(np.mean(List))
    shortest_path.append(np.max(List))
    shortest_path.append(np.min(List))
    shortest_path.append(np.median(List))
    shortest_path.append(np.std(List))

    return shortest_path

def closeness_centrality(G):

    List=list(nx.closeness_centrality(G).values())
    closeness_centrality=[]
    closeness_centrality.append(np.mean(List))
    closeness_centrality.append(np.max(List))
    closeness_centrality.append(np.min(List))
    closeness_centrality.append(np.median(List))
    closeness_centrality.append(np.std(List))
    
    return closeness_centrality

def betweeness_centrality(G):

    List=list(nx.betweenness_centrality(G.to_undirected()).values())
    betweeness_centrality=[]
    betweeness_centrality.append(np.mean(List))
    betweeness_centrality.append(np.max(List))
    betweeness_centrality.append(np.min(List))
    betweeness_centrality.append(np.median(List))
    betweeness_centrality.append(np.std(List))

    return betweeness_centrality

def degree_centrality(G):

    List=list(nx.degree_centrality(G).values())
    degree_centrality=[]
    degree_centrality.append(np.mean(List))
    degree_centrality.append(np.max(List))
    degree_centrality.append(np.min(List))
    degree_centrality.append(np.median(List))
    degree_centrality.append(np.std(List))

    return degree_centrality


def Feature_extraction(path):
    G=create_graph(path)
    global inValid
    feature=[]
    # append #nodes & # edges
    feature.append(G.number_of_nodes())
    feature.append(G.number_of_edges())

    # append Density
    feature.append(get_density(G))
    if inValid==0:
    # append Closeness Centrality
      for i in closeness_centrality(G):
          feature.append(i)

    # append Betweeness Centrality
      for i in betweeness_centrality(G):
          feature.append(i)

    # append Degree Centrality
      for i in degree_centrality(G):
          feature.append(i)

    # append Shortest Path
      for i in shortest_path(G):
          feature.append(i)

    return np.array(feature)
    
def main(args):
    global inValid
    label_dict = {0:'BenignWare', 1:'Malware'}
    feature=Feature_extraction(args.input_path)
    if inValid==0:
    ## 將底下model path 改成以train 完的model即可做檢測。
        #Model=jb.load('/home/Wu/NICT/Master/ML_Task/Comparison/Model_Training/Model_svg2/GraphTheory_RF')
        dir = pathlib.Path(__file__).parent.absolute()
        Model=jb.load(str(dir) + '/Model_detection/GraphTheory_detection_KNN')
        #print(Model)
        y_predicted = Model.predict(feature.reshape(1, -1))
        print(y_predicted[0])
    else:
        #print("can't extract feature")
        print(2)
if __name__=='__main__':
    args=parameter_parser()
    main(args)