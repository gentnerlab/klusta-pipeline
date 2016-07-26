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

    # probes A1x32-Poly3-xmm-25s-yyy
    elif 'A1x32-Poly3' in probe and '25s' in probe:
        channel_groups = {
            # Shank index.
            0: {   
                # List of channels to keep for spike detection.
                'channels': s.values(),

                # 2D positions of the channels
                'geometry': {
                    s[17]: (18, 275), # column 1
                    s[16]: (18, 250), 
                    s[18]: (18, 225),
                    s[15]: (18, 200),
                    s[19]: (18, 175),
                    s[14]: (18, 150),
                    s[20]: (18, 125),
                    s[13]: (18, 100),
                    s[21]: (18, 75),
                    s[12]: (18, 50),
                    s[22]: (18, 25),
                    s[11]: (18, 0), 
                    s[10]: (0, 237), # column 0
                    s[9]: (0, 212), 
                    s[8]: (0, 187), 
                    s[7]: (0, 162), 
                    s[6]: (0, 137), 
                    s[5]: (0, 112), 
                    s[4]: (0, 87), 
                    s[3]: (0, 62), 
                    s[2]: (0, 37),  
                    s[1]: (0, 12),   
                    s[23]: (36, 237), # column 3
                    s[24]: (36, 212), 
                    s[25]: (36, 187), 
                    s[26]: (36, 162), 
                    s[27]: (36, 137), 
                    s[28]: (36, 112), 
                    s[29]: (36, 87), 
                    s[30]: (36, 62), 
                    s[31]: (36, 37),  
                    s[32]: (36, 12)
                }
            }
        }

    # probes A1x32-Edge-xmm-20s-yyy
    elif 'A1x32-Edge' in probe and '20' in probe:
        channel_groups = {
            # Shank index.
            0: {   
                # List of channels to keep for spike detection.
                'channels': s.values(),

                # 2D positions of the channels
                'geometry': {
                    s[1]: (0, 0), # column 1
                    s[2]: (0, 20), 
                    s[3]: (0, 40),
                    s[4]: (0, 60),
                    s[5]: (0, 80),
                    s[6]: (0, 100),
                    s[7]: (0, 120),
                    s[8]: (0, 140),
                    s[9]: (0, 160),
                    s[10]: (0, 180),
                    s[11]: (0, 200),
                    s[12]: (0, 220), 
                    s[13]: (0, 240), # column 0
                    s[14]: (0, 260), 
                    s[15]: (0, 280), 
                    s[16]: (0, 300), 
                    s[17]: (0, 320), 
                    s[18]: (0, 340), 
                    s[19]: (0, 360), 
                    s[20]: (0, 380), 
                    s[21]: (0, 400),  
                    s[22]: (0, 420),   
                    s[23]: (0, 440), # column 3
                    s[24]: (0, 460), 
                    s[25]: (0, 480), 
                    s[26]: (0, 500), 
                    s[27]: (0, 520), 
                    s[28]: (0, 540), 
                    s[29]: (0, 560), 
                    s[30]: (0, 580), 
                    s[31]: (0, 600),  
                    s[32]: (0, 620)
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
    elif probe=='A1x16-5mm-50-177-H16':
        channel_groups = {
            # Shank index.
            0: {   
                # List of channels to keep for spike detection.
                'channels': s.values(),
                
                # 2D positions of the channels, in microns.
                # NOTE: For visualization purposes
                # in KlustaViewa, the unit doesn't matter.
                'geometry': {
                    s[1]: (0, 0),
                    s[16]: (0, 50),
                    s[2]: (0, 100),
                    s[15]: (0, 150),
                    s[3]: (0, 200),
                    s[14]: (0, 250),
                    s[4]: (0, 300),
                    s[13]: (0, 350),
                    s[5]: (0, 400),
                    s[12]: (0, 450),
                    s[6]: (0, 500),
                    s[11]: (0, 550),
                    s[7]: (0, 600),
                    s[10]: (0, 650),
                    s[8]: (0, 700),
                    s[9]: (0, 750),
                }
            }
        }
    elif probe=='Buzsaki32':
        channel_groups = {}
        for i in range(4):
            channel_groups[i] = {}
            channel_groups[i]['geometry'] = {
                s[5 + i*8]: (0 + 200 * i, 0),
                s[4 + i*8]: (-8.5 + 200 * i, 20),
                s[6 + i*8]: (8.5 + 200 * i, 40),
                s[3 + i*8]: (-12.5 + 200 * i, 60),
                s[7 + i*8]: (12.5 + 200 * i, 80),
                s[2 + i*8]: (-16.5 + 200 * i, 100),
                s[8 + i*8]: (16.5 + 200 * i, 120),
                s[1 + i*8]: (-20.5 + 200 * i, 140),
            }
            channel_groups[i]['channels'] = channel_groups[i]['geometry'].keys()
    elif 'a4x4-4mm200' in probe:
        channel_groups = {}
        for i in range(4):
            channel_groups[i] = {}
        channel_groups[0]['geometry'] = {
            s[6]: (0,0),
            s[2]: (0,200),
            s[3]: (0,400),
            s[1]: (0,600),
        }
        channel_groups[1]['geometry'] = {
            s[5]: (200,0),
            s[8]: (200,200),
            s[4]: (200,400),
            s[7]: (200,600),
        }
        channel_groups[2]['geometry'] = {
            s[9]: (400,0),
            s[12]: (400,200),
            s[10]: (400,400),
            s[13]: (400,600),
        }
        channel_groups[3]['geometry'] = {
            s[15]: (600,0),
            s[11]: (600,200),
            s[16]: (600,400),
            s[14]: (600,600),
        }
        for i in range(4):
            channel_groups[i]['channels'] = channel_groups[i]['geometry'].keys()
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
