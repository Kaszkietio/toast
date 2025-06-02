import React, { useEffect, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";

function App() {
  let nodes = []
  let links = [];
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/traffic");

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
          vx: oldNode?.vx,
          vy: oldNode?.vy,
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
      console.log("graphData state:", graphData);
    };

    return () => socket.close();
  }, []);

  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <ForceGraph2D
        graphData={graphData}
        nodeLabel={(node) => `Crossroad: ${node.id}`}
        linkLabel={(link) => `Traffic: ${link.traffic}`}
        linkColor={(link) => {
          const t = link.traffic || 0;
          return t > 15 ? "red" : t > 5 ? "orange" : t > 0 ? "green" : "black";
        }}
        nodeAutoColorBy="id"
        linkLineDash={link => link.green_light > 0 ? [2, 2] : []}
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        linkCurvature={0.25}
        linkWidth={4}
      />
    </div>
  );
}

export default App;
