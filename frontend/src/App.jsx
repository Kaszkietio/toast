import React, { useEffect, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';

function App() {
  const fgRef = useRef();
  let nodes = []
  let links = [];
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/traffic")
    socket.onopen = () => {
      console.log("WebSocket connection established");
      socket.send("get_graph");
    }

    const interval = setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send("get_graph");
      }
    }, 1000);

    socket.onmessage = (event) => {
      const incoming = JSON.parse(event.data);
      // if (incoming["event"] !== undefined) {
      //   console.log("Event received:", incoming);
      // }
      // console.log("Received data:", incoming.special_vehicle);

      // Attempt to access old nodes
      const existingNodes = nodes.length ? nodes : [];

      const mergedNodes = incoming.nodes.map((newNode) => {
        const oldNode = existingNodes.find((n) => n.id === newNode.id);
        return {
          ...newNode,
          x: oldNode?.x,
          y: oldNode?.y,
          fx: oldNode?.x,
          fy: oldNode?.y,
        };
      });

      nodes = [...mergedNodes]
      links =incoming.links.map(newLink => {
        const existingSource = nodes.find(n => n.id === newLink.source);
        const existingTarget = nodes.find(n => n.id === newLink.target);
        return {
          ...newLink,
          source: existingSource ? existingSource.id : newLink.source,
          target: existingTarget ? existingTarget.id : newLink.target,
        };
      })

      setGraphData({
        nodes: nodes,
        links: links,
      });
      // console.log("links", links)
      // console.log("graphData state:", graphData);
    };

    return () => {
      clearInterval(interval);
      socket.close()
    };
  }, []);

  useEffect(() => {
    if (fgRef.current) {
      fgRef.current.d3Force('charge')?.strength(-10); // Repulsion
      fgRef.current.d3Force('link')?.distance(100);     // Link length
    }
  }, [graphData]); // Re-apply forces when graph updates

  const spawnAmbulance = () => {
    fetch('http://localhost:8000/spawn-ambulance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {}
    });
  };

  let currentData = []
  let special_vehicles = []
  const [data, setData] = useState([]);
  const [specialVehicle, setSpecialVehicle] = useState([]);

  useEffect(() => {
    const fetchMetrics = async () => {
      const res = await fetch('http://localhost:8000/metrics');
      const json = await res.json();
      // console.log("Metrics data:", json);
      currentData = [...currentData, // Keep previous data
        {
        Time: Number(json.Time).toFixed(2), // Convert time to a fixed decimal
        TotalTraffic: Number(json.TotalTraffic).toFixed(2), // Convert total traffic to a fixed decimal
        // AverageTraffic: Number(json.AverageTraffic).toFixed(2), // Convert average traffic to a fixed decimal
      }]
      special_vehicles = [...special_vehicles, // Keep previous special vehicles
        ...(json.SpecialVehicles || [])
      ]
      // const plotData = json.Time.map((t, i) => (,
      // }));
      console.log("Current data:", currentData);
      console.log("Special vehicles:", special_vehicles);
      setData(currentData);
      setSpecialVehicle(special_vehicles);
    };

    const interval = setInterval(fetchMetrics, 1000);
    return () => clearInterval(interval);
  }, []);

  const [ambulancePriority, setAmbulancePriority] = useState(true);
  const [adaptiveLights, setAdaptiveLights] = useState(true);

  const toggleSpecialVehicleCompliance = async () => {
    const newState = !ambulancePriority;
    setAmbulancePriority(newState);
    await fetch("http://localhost:8000/config/ambulance_priority", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newState),
    });
  };

  const toggleAdaptiveLights = async () => {
    const newState = !adaptiveLights;
    setAdaptiveLights(newState);
    await fetch("http://localhost:8000/config/adaptive_lights", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newState),
    });
  };

  const saveMetrics = async () => {
    await fetch("http://localhost:8000/save/metrics", { method: "POST"});
  };

  const car_accident = (link) => {
    fetch("http://localhost:8000/simulate-accident", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: link.source.id, target: link.target.id }),
    }).then(() => {
      console.log(`Accident triggered on link ${link.source.id} -> ${link.target.id}`);
    })
  }


  return (
    <div style={{ display: 'flex', height: '100vh', padding: '20px'}}>
      <div style={{ flex: 1, padding: 0 }}>
        <h3>Traffic & Waiting Cars</h3>
        <LineChart width={600} height={300} data={data}>
          <CartesianGrid stroke="#ccc" />
          <XAxis dataKey="Time" />
          <YAxis />
          <Tooltip />
          <Line type="linear" dataKey="TotalTraffic" stroke="#8884d8" name="Total Traffic" />
          <Legend layout="vertical" verticalAlign="top" align="right" />
        </LineChart>
        <h3>Ambulance Travel Times</h3>
        <BarChart width={600} height={250} data={specialVehicle}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="id" />
          <YAxis label={{ value: 'Time (s)', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          <Bar dataKey="time_passed" fill="#ffc658" name="Travel Time (s)" />
        </BarChart>
      </div>
      <div style={{ flex: 1 }}>
        <button onClick={spawnAmbulance} style={{ padding: '10px'}}>🚑 Spawn Special Vehicle</button>

        <button onClick={saveMetrics} style={{ padding: '10px'}}>💾 Save Metrics</button>
        <div style={{ display: 'flex', gap: '2rem', marginBottom: '1rem' }}>
        <label>
          <input type="checkbox" checked={ambulancePriority} onChange={toggleSpecialVehicleCompliance} />
          🚑 Special Vehicle Light Priority
        </label>
        <label>
          <input type="checkbox" checked={adaptiveLights} onChange={toggleAdaptiveLights} />
          💡 Adaptive Traffic Lights
        </label>
      </div>
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeLabel={(node) => `Crossroad: ${node.id}`}
          nodeColor={(node) => {
            if (node.id == '0') {
              return 'red';
            }
            if (node.id == '5') {
              return 'blue';
            }
            return 'lightgray';
          }}
          linkLabel={(link) => `Traffic: ${link.traffic} ` +
            `Light: ${Number(link.light_duration).toFixed(2)}s` +
            ` Throughput: ${Number(link.throughput).toFixed(2)}` +
            (link.special_vehicle != null ? ` Time left: ${Number(link.special_vehicle.time_left).toFixed(2)}` : '')}
          linkColor={(link) => {
            let traffic = link.traffic;
            let throughput = link.throughput;
            const t = throughput == 0.0 ? parseFloat('inf') : (traffic / throughput);
            return t > 4 ? "red" : t > 2 ? "orange" : t > 0 ? "green" : "black";
          }}
          // nodeAutoColorBy="id"
          linkDirectionalParticles={link => link.green_light ? 1 : 0}
          linkDirectionalParticleWidth={10}
          linkCurvature={0.25}
          linkWidth={(link) => link.throughput / 3}
          linkCanvasObjectMode={() => "after"}
          linkCanvasObject={(link, ctx, globalScale) => {
            const label = `${link.special_vehicle != undefined ? '🚑 | ' : ''}${link.traffic ?? 0} ` +
              `| ⏱ ${Number(link.light_duration).toFixed(2) ?? '-'} | ${link.green_light > 0 ? '🟢' : '🔴'}`;
            const start = link.source;
            const end = link.target;

            if (typeof start !== 'object' || typeof end !== 'object') return;

            // Calculate mid-point
            const x = (start.x + end.x) / 2;
            const y = (start.y + end.y) / 2;

            const fontSize = 14 / globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.fillStyle = 'rgba(232, 222, 222, 0.8)';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(label, x, y);
          }}
          linkLineDash={link => (link.special_vehicle != null ? [2, 2] : [])}
          linkDirectionalArrowLength={5}
          linkDirectionalArrowRelPos={1}
          onLinkClick={car_accident}
        />
      </div>
    </div>
  );
}

export default App;
