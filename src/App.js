import AutoSizer from 'react-virtualized/dist/es/AutoSizer';
import React, {Component} from 'react';
import Polygon from './data/Polygon';
import {hsvToHex} from "colorsys";
import MapGL from 'react-map-gl';
import Line from './data/Line';
import 'antd/dist/antd.css';
import axios from 'axios';
import {DatePickerBar} from "./components/DatePickerBar";

const MAPBOX_TOKEN = 'pk.eyJ1IjoiZ29sZGZvcjEiLCJhIjoiY2p4c3BzeThxMGpzejNtbzF5YmgxM2ttOSJ9.f2knfkaI5bt5avgiS5qDlw'; // eslint-disable-line


export default class App extends Component {

    constructor(props) {
        super(props);

        this.state = {
            viewport: {
                latitude: 44.89,
                longitude: 37.31,
                zoom: 12,
                bearing: 0,
                pitch: 0
            },
            earthquakes: null
        };

        this._mapRef = React.createRef();
        this.handleMapLoaded = this.handleMapLoaded.bind(this);
    };

    makePolygonLayer = (id, source, color) => {
        return {
            id, source,
            type: 'fill',
            layout: {},
            paint: {
                'fill-color': color,
                'fill-opacity': 0.2
            }
        }
    };

    makeLineLayer = (id, source, color) => {
        return {
            id, source,
            type: 'line',
            layout: {
                'line-join': 'round',
                'line-cap': 'round'
            },
            paint: {
                'line-color': color,
                'line-width': 3
            }
        }
    };

    _onViewportChange = (viewport) => this.setState({viewport});

    getMap = () => this._mapRef.current ? this._mapRef.current.getMap() : null;

    getColor = (data) => {
        const map = this.getMap();
        const MIN = Math.min.apply(null, data);
        const MAX = Math.max.apply(null, data);
        for (let i = 0; i < 5; i++) {
            const color = hsvToHex({h: this.mapValue(data[i], MIN, MAX, -120, 0), s: 100, v: 100});
            console.log(color);
            const str = i.toString();
            map.addSource(('Polygon' + str), {type: 'geojson', data: Polygon[i]});
            map.addLayer(this.makePolygonLayer(('Polygon' + str), ('Polygon' + str), color));
            map.addSource(('Line' + str), {type: 'geojson', data: Line[i]});
            map.addLayer(this.makeLineLayer(('Line' + str), ('Line' + str), color));
        }
    };

    mapValue = (x, in_min, in_max, out_min, out_max) => (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;

    handleMapLoaded = () => {
        this.refreshData([0, 10000000000])
    };

    refreshData = (dates) => {
        axios.get('/api/clusters', {
                params: {
                    start: dates[0],
                    end: dates[1]
                }
            }
        ).then((response) => {
            // handle response
            let array = [];
            console.log('Data response: ', response.data);
            console.log(Polygon);
            Polygon.forEach((item) => {
                response.data.forEach((i) => {
                    if (i._id === item.features[0].properties.name) {
                        array.push(i.count);
                    }
                });
            });
            this.getColor(array);
        }).catch((error) => {
            // handle error
            console.log('Data response error: ', error);
        });
    };

    render() {
        return (
            <div style={{position: 'absolute', width: '100%', height: '100%', minHeight: '70vh'}}>
                <AutoSizer>
                    {({height, width}) => (
                        <MapGL
                            ref={this._mapRef}
                            {...this.state.viewport}
                            width={width}
                            height={height}
                            mapStyle={'mapbox://styles/mapbox/light-v10'}
                            onViewportChange={this._onViewportChange}
                            mapboxApiAccessToken={MAPBOX_TOKEN}
                            onLoad={this.handleMapLoaded}
                        />)}
                </AutoSizer>
                <DatePickerBar onSearch={(x) => this.refreshData(x)}/>
            </div>
        );
    }
}
