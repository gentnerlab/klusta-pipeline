from scipy import spatial
from klusta_pipeline import MAX_CHANS

def load_sitemap(sitelist):
    # site:channel
    s = {site:None for site in range(MAX_CHANS)}
    with open(sitelist,'r') as f:
        for line in f:
            indx,_,site = line.split(',')
            s[int(site)] = int(indx)
    return s

def get_channel_groups(probe,s):
    if probe=='A1x32-Poly3-6mm-50':
        channel_groups = {
            # Shank index.
            0: {   
                # List of channels to keep for spike detection.
                'channels': s.values(),

                # 2D positions of the channels
                'geometry': {
                    s[3]: (0,500), # column 0
                    s[2]: (0,450),
                    s[1]: (0,400),
                    s[4]: (0,350),
                    s[5]: (0,300),
                    s[6]: (0,250),
                    s[7]: (0,200),
                    s[8]: (0,150),
                    s[9]: (0,100),
                    s[10]: (0,50),
                    s[11]: (0,0), 
                    s[17]: (50,450), # column 1
                    s[16]: (50,400), 
                    s[18]: (50,350), 
                    s[15]: (50,300), 
                    s[19]: (50,250), 
                    s[14]: (50,200), 
                    s[20]: (50,150), 
                    s[13]: (50,100), 
                    s[21]: (50,50),  
                    s[12]: (50,0),   
                    s[30]: (100,500), # column 2
                    s[31]: (100,450),
                    s[32]: (100,400),
                    s[29]: (100,350),
                    s[28]: (100,300),
                    s[27]: (100,250),
                    s[26]: (100,200),
                    s[25]: (100,150),
                    s[24]: (100,100),
                    s[23]: (100,50), 
                    s[22]: (100,0),  
                }
            }
        }

    elif probe=='A1x16-5mm-50':
        channel_groups = {
            # Shank index.
            0: {   
                # List of channels to keep for spike detection.
                'channels': s.values(),
                
                # 2D positions of the channels, in microns.
                # NOTE: For visualization purposes
                # in KlustaViewa, the unit doesn't matter.
                'geometry': {
                    s[6]: (0, 0),
                    s[11]: (0, 50),
                    s[3]: (0, 100),
                    s[14]: (0, 150),
                    s[1]: (0, 200),
                    s[16]: (0, 250),
                    s[2]: (0, 300),
                    s[15]: (0, 350),
                    s[5]: (0, 400),
                    s[12]: (0, 450),
                    s[4]: (0, 500),
                    s[13]: (0, 550),
                    s[7]: (0, 600),
                    s[10]: (0, 650),
                    s[8]: (0, 700),
                    s[9]: (0, 750),
                }
            }
        }
    else:
        raise Exception('probe not found')

    return channel_groups

def get_graph_from_geometry(geometry):
    # let's transform the geometry into lists of channel names and coordinates
    chans,coords = zip(*[(ch,xy) for ch,xy in geometry.iteritems()])
    
    # we'll perform the triangulation and extract the 
    try:
        tri = spatial.Delaunay(coords)
    except:
        x,y = zip(*coords)
        coords = list(coords)
        coords.append((max(x)+1,max(y)+1))
        tri = spatial.Delaunay(coords)
    
    # then build the list of edges from the triangulation
    indices, indptr = tri.vertex_neighbor_vertices
    print indices, indptr
    edges = []
    for k in range(indices.shape[0]-1):
        for j in indptr[indices[k]:indices[k+1]]:
            try:
                edges.append((chans[k],chans[j]))
            except IndexError:
                # ignore dummy site
                pass
    return edges

def clean_dead_channels(channel_groups):
    new_group = {}
    for gr, group in channel_groups.iteritems():
        new_group[gr] = {
            'channels': [],
            'geometry': {}
        }
        new_group[gr]['channels'] = [ch for ch in group['channels'] if ch is not None]
        new_group[gr]['geometry'] = {ch:xy for (ch,xy) in group['geometry'].iteritems() if ch is not None}
        
    return new_group

def build_geometries(channel_groups):
    for gr, group in channel_groups.iteritems():
        group['graph'] = get_graph_from_geometry(group['geometry'])
    return channel_groups

def load_probe(filename):
    prb = {}
    execfile(filename, {}, prb)
    return prb['channel_groups']

def plot_channel_groups(channel_groups):
    import matplotlib.pyplot as plt 
    n_shanks = len(channel_groups)

    f,ax = plt.subplots(1,n_shanks,squeeze=False)
    for sh in range(n_shanks):
        coords = [xy for ch,xy in channel_groups[sh]['geometry'].iteritems()]
        x,y = zip(*coords)
        ax[sh,0].scatter(x,y,color='0.2')

        for pr in channel_groups[sh]['graph']:
            points = [channel_groups[sh]['geometry'][p] for p in pr]
            ax[sh,0].plot(*zip(*points),color='k',alpha=0.2)

        ax[sh,0].set_xlim(min(x)-10,max(x)+10)
        ax[sh,0].set_ylim(min(y)-10,max(y)+10)
        ax[sh,0].set_xticks([])
        ax[sh,0].set_yticks([])
        ax[sh,0].set_title('group %i'%sh)
            
        ax[sh,0].set_aspect('equal')
    plt.show()


def _get_args():
    import argparse
    parser = argparse.ArgumentParser(description='gdisplay the geometry defined in a probe file')
    parser.add_argument('probefile',type=str, 
                       help='the probe file')
    return parser.parse_args()

def _display():
    args = _get_args()
    channel_groups = load_probe(args.probefile)
    plot_channel_groups(channel_groups)
