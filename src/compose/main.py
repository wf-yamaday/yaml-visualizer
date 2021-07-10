import yaml
from graphviz import Graph


def dispatch(filename):
    # yamlファイルの読み込み
    with open(filename) as s:
        data = yaml.safe_load(s)

    g = Graph(format='png')
    g.attr(rankdir='LR')
    g.attr(compound='true')
    # 基底のnodeを作成
    for k in data.keys():
        if k == 'version':
            continue
        g.node(k)

    # volumesのnodeを作成
    volumes_node = []
    type = 'volumes'
    if type in data.keys():
        for d in data[type]:
            g.node(d, shape='cylinder')
            g.edge(type, d)
            volumes_node.append(d)

    # networksのnodeを作成
    networks_node = []
    type = 'networks'
    if type in data.keys():
        for d in data[type]:
            g.node(d)
            g.edge(type, d)
            networks_node.append(d)

    host_volume_dict = {}
    host_port_dict = {}
    # servicesのnodeを作成
    type = 'services'
    if type in data.keys():
        # 各サービスでサブグラフを作成
        for d in data[type]:
            subgraph_name = 'cluster_{}'.format(d)
            # コンテナ名を取得
            container_name = 'default_{}'.format(d)
            if 'container_name' in data[type][d]:
                container_name = data[type][d]['container_name']
            else:
                print('[warning] Reccommend set container_name property.')

            # volumeの設定を取得
            container_volume_dict = {}
            if 'volumes' in data[type][d]:
                volumes_list = data[type][d]['volumes']
                for v in volumes_list:
                    a = v.split(':')
                    if len(a) > 1:
                        container_volume = '{}_{}'.format(container_name, a[1])
                        if a[0] in volumes_node:
                            container_volume_dict[a[1]] = a[0]
                        else:
                            container_volume_dict[a[1]] = container_volume
                            if a[0] in host_volume_dict.keys():
                                host_volume_dict[a[0]].append(container_volume)
                            else:
                                host_volume_dict[a[0]] = [container_volume]
            # networkの設定を取得
            container_networks = []
            if 'networks' in data[type][d]:
                networks_list = data[type][d]['networks']
                for n in networks_list:
                    if n in networks_node:
                        container_networks.append(n)

            # 環境変数の取得
            environment_values = ''
            if 'environment' in data[type][d]:
                environment_values = '\n'.join(
                    list(data[type][d]['environment'].keys()))

            # ポート情報の取得
            container_port_dict = {}
            if 'ports' in data[type][d]:
                ports_list = data[type][d]['ports']
                for p in ports_list:
                    a = p.split(':')
                    if len(a) > 1:  # TODO 単体で指定された場合の処理
                        container_port = '{}_{}'.format(
                            container_name, a[1])
                        container_port_dict[a[1]] = container_port
                        host_port_dict[a[0]] = container_port

            # グラフ描画（コンテナ）
            with g.subgraph(name=subgraph_name) as sg:
                sg.attr("graph", style='filled', fillcolor='lightgrey')
                sg.attr(label=container_name)
                sg.node_attr.update(style='filled', color='white')
                # サービス名のnodeを作成
                sg.node(d)
                # volumeのnodeを作成
                volume_subgraph_name = '{}_volume'.format(subgraph_name)
                with sg.subgraph(name=volume_subgraph_name) as vsg:
                    vsg.attr(label='volumes')
                    for p in container_volume_dict.keys():
                        if container_volume_dict[p] in volumes_node:
                            node_name = '{}_{}'.format(container_name, p)
                            vsg.node(
                                node_name, p, shape='folder')
                            g.edge(node_name,
                                   container_volume_dict[p])
                            continue
                        vsg.node(container_volume_dict[p], p, shape='folder')
                # networksとのedgeを作成
                for n in container_networks:
                    g.edge(d, n, ltail=subgraph_name)
                # 環境変数の設定項目を記載
                if environment_values != '':
                    sg.node(environment_values, shape='note')
                # portのnodeを作成
                port_subgraph_name = '{}_port'.format(subgraph_name)
                with sg.subgraph(name=port_subgraph_name) as psg:
                    psg.attr(label='ports')
                    for p in container_port_dict.keys():
                        psg.node(container_port_dict[p], p, shape='terminator')
            g.edge(type, d)

    # グラフ描画（ホスト）
    host_subgraph_name = '{}_host'.format(subgraph_name)
    with g.subgraph(name=host_subgraph_name) as hsg:
        hsg.attr(label='host machine')
        # ホストのvolumeのnodeを作成
        volume_host_subgraph_name = '{}_volume'.format(host_subgraph_name)
        with hsg.subgraph(name=volume_host_subgraph_name) as vhsg:
            vhsg.attr(label='volumes')
            for p in host_volume_dict.keys():
                if not p in volumes_node:
                    vhsg.node(p, shape='folder')
                    for d in host_volume_dict[p]:
                        g.edge(p, d)
        # ホストのportのnodeを作成
        port_host_subgraph_name = '{}_port'.format(host_subgraph_name)
        with hsg.subgraph(name=port_host_subgraph_name) as phsg:
            phsg.attr(label='ports')
            for p in host_port_dict.keys():
                phsg.node(p, shape='terminator')
                g.edge(p, host_port_dict[p])

    # ファイルに書き出し
    return g
