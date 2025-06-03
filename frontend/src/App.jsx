import React, { useEffect, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";

function App() {
  const fgRef = useRef();
  let nodes = []
  let links = [];
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/traffic");
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
      console.log(links)
      console.log("graphData state:", graphData);
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

  return (
    <div style={{ width: "100vw", height: "100vh" }}>
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
        linkLabel={(link) => `Traffic: ${link.traffic} Light: ${link.light_duration}s Throughput: ${Number(link.throughput).toFixed(2)}`}
        linkColor={(link) => {
          const t = link.traffic || 0;
          return t > 80 ? "red" : t > 40 ? "orange" : t > 0 ? "green" : "black";
        }}
        // nodeAutoColorBy="id"
        linkLineDash={link => link.green_light > 0 ? [2, 2] : []}
        linkDirectionalArrowLength={5}
        linkDirectionalArrowRelPos={1}
        linkCurvature={0.25}
        linkWidth={4}
        linkCanvasObjectMode={() => "after"}
        linkCanvasObject={(link, ctx, globalScale) => {
          const label = `🚗 ${link.traffic ?? 0} | ⏱ ${link.light_duration ?? '-'} | ${link.green_light > 0 ? '🟢' : '🔴'}`;
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
      />
    </div>
  );
}

export default App;
