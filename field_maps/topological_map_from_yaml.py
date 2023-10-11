
import yaml 

import pickers_model.strawberry_field.topological_map as tm

def read_yaml_datum_file( datum_file ): 
    
    f = open( datum_file )
    data = yaml.safe_load( f )
    
    datum_longitude = data['datum_longitude']
    datum_latitude = data['datum_latitude']

    print( datum_longitude, datum_latitude )
    return datum_longitude, datum_latitude

def read_yaml( yaml_file ):    

    f = open( yaml_file )
    data = yaml.safe_load( f ) 
    
    topological_map = tm.TopologicalMap( )
        
    for n in data['nodes']:
        print( n['meta']['node'], n['node']['pose']['position']['x'], n['node']['pose']['position']['y'] ) #, n['node']['pose']['position']['x'] + 1, n['node']['pose']['position']['y'] + 1 )
        
        new_node = tm.TMNode( n['node']['pose']['position']['x'], n['node']['pose']['position']['y'] ) 
        new_node.node_id = n['meta']['node']
        topological_map.add_node( new_node )
    
    for n in data['nodes']: 
        
        n0 = topological_map.find_node_by_id( n['meta']['node'] ) 
        for e in n['node']['edges']:
            n1 = topological_map.find_node_by_id( e['node'] )
            topological_map.add_edge( n0, n1, e['edge_id'] )
    
    for edge in topological_map.edges:
        print( edge.edge_id, edge.nodes[0].node_id, edge.nodes[1].node_id )
    
    return topological_map
    
def create_tmap_from_yamls( yaml_file, datum_file, longdif_to_meters, latdif_to_meters ): 
    
    tmap = read_yaml( yaml_file )
    datum_longitude, datum_latitude = read_yaml_datum_file( datum_file )
    
    for n in tmap.nodes: 
        
        n.longitude = datum_longitude + n.tmap_x / longdif_to_meters 
        n.latitude = datum_latitude + n.tmap_y / latdif_to_meters
    
    return tmap
    
if __name__ == '__main__' : 
    
    datumfile = '../TopologicalMaps/datum.yaml'
    # filename = '../TopologicalMaps/tmap.yaml'
    filename = '../TopologicalMaps/network.yaml'
    
    longdif_to_meters = 66.5232 / 0.001
    latdif_to_meters = 111.2298 / 0.001
        
    create_tmap_from_yamls( filename, datumfile, longdif_to_meters, latdif_to_meters )
