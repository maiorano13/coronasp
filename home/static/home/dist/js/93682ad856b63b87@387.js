// https://observablehq.com/@paulgarcia89/diverging-bar-chart@387
export default function define(runtime, observer) {
  const main = runtime.module();
  const fileAttachments = new Map([["state-population-2010-2019.tsv",new URL("./files/553ece9b37cf5bc5cd7da5709585f70ecddac30e8df28cf16a0689d4e2ace1c35f6d18033cc2e4920ac7920b2549211e3b9f4b73460bf5c19e01a64051403866",import.meta.url)]]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
  main.variable(observer()).define(["md"], function(md){return(
md`# Diverging Bar Chart

A diverging bar chart can show negative values as well as positive ones. Bars are positioned by their top-left corner and cannot have a negative width; thus if the value is positive, it determines the right edge, while if it’s negative, it determines the left. This chart shows estimated change in population from 2010 to 2019.`
)});
  main.variable(observer("viewof metric")).define("viewof metric", ["html"], function(html)
{
  const form = html`<form style="font: 12px var(--sans-serif); display: flex; height: 33px; align-items: center;">
  <label style="margin-right: 1em; display: inline-flex; align-items: center;">
    <input type="radio" name="radio" value="absolute" style="margin-right: 0.5em;"> Absolute change
  </label>
  <label style="margin-right: 1em; display: inline-flex; align-items: center;">
    <input type="radio" name="radio" value="relative" style="margin-right: 0.5em;" checked> Relative change
  </label>
</form>`;
  form.onchange = () => form.dispatchEvent(new CustomEvent("input")); // Safari
  form.oninput = () => form.value = form.radio.value;
  form.value = form.radio.value;
  return form;
}
);
  main.variable(observer("metric")).define("metric", ["Generators", "viewof metric"], (G, _) => G.input(_));
  main.variable(observer("chart")).define("chart", ["d3","width","height","data","x","y","format","xAxis","yAxis"], function(d3,width,height,data,x,y,format,xAxis,yAxis)
{
  const svg = d3.create("svg")
      .attr("viewBox", [0, 0, width, height]);
  
  svg.append("g")
    .selectAll("rect")
    .data(data)
    .join("rect")
      .attr("fill", d => d3.schemeSet1[d.value > 0 ? 1 : 0])
      .attr("x", d => x(Math.min(d.value, 0)))
      .attr("y", (d, i) => y(i))
      .attr("width", d => Math.abs(x(d.value) - x(0)))
      .attr("height", y.bandwidth());

  svg.append("g")
      .attr("font-family", "sans-serif")
      .attr("font-size", 10)
    .selectAll("text")
    .data(data)
    .join("text")
      .attr("text-anchor", d => d.value < 0 ? "end" : "start")
      .attr("x", d => x(d.value) + Math.sign(d.value - 0) * 4)
      .attr("y", (d, i) => y(i) + y.bandwidth() / 2)
      .attr("dy", "0.35em")
      .text(d => format(d.value));

  svg.append("g")
      .call(xAxis);

  svg.append("g")
      .call(yAxis);

  return svg.node();
}
);
  main.variable(observer("data")).define("data", ["d3","FileAttachment","metric"], async function(d3,FileAttachment,metric){return(
d3.tsvParse(await FileAttachment("state-population-2010-2019.tsv").text(), ({State: name, "2010": value0, "2019": value1}) => ({name, value: metric === "absolute" ? value1 - value0 : (value1 - value0) / value0})).sort((a, b) => d3.ascending(a.value, b.value))
)});
  main.variable(observer("x")).define("x", ["d3","data","margin","width"], function(d3,data,margin,width){return(
d3.scaleLinear()
    .domain(d3.extent(data, d => d.value))
    .rangeRound([margin.left, width - margin.right])
)});
  main.variable(observer("y")).define("y", ["d3","data","margin","height"], function(d3,data,margin,height){return(
d3.scaleBand()
    .domain(d3.range(data.length))
    .rangeRound([margin.top, height - margin.bottom])
    .padding(0.1)
)});
  main.variable(observer("xAxis")).define("xAxis", ["margin","d3","x","width","tickFormat"], function(margin,d3,x,width,tickFormat){return(
g => g
    .attr("transform", `translate(0,${margin.top})`)
    .call(d3.axisTop(x).ticks(width / 80).tickFormat(tickFormat))
    .call(g => g.select(".domain").remove())
)});
  main.variable(observer("yAxis")).define("yAxis", ["x","d3","y","data"], function(x,d3,y,data){return(
g => g
    .attr("transform", `translate(${x(0)},0)`)
    .call(d3.axisLeft(y).tickFormat(i => data[i].name).tickSize(0).tickPadding(6))
    .call(g => g.selectAll(".tick text").filter(i => data[i].value < 0)
        .attr("text-anchor", "start")
        .attr("x", 6))
)});
  main.variable(observer("format")).define("format", ["d3","metric"], function(d3,metric){return(
d3.format(metric === "absolute" ? "+,d" : "+,.0%")
)});
  main.variable(observer("tickFormat")).define("tickFormat", ["metric","d3","format"], function(metric,d3,format){return(
metric === "absolute" ? d3.formatPrefix("+.1", 1e6) : format
)});
  main.variable(observer("barHeight")).define("barHeight", function(){return(
25
)});
  main.variable(observer("height")).define("height", ["data","barHeight","margin"], function(data,barHeight,margin){return(
Math.ceil((data.length + 0.1) * barHeight) + margin.top + margin.bottom
)});
  main.variable(observer("margin")).define("margin", function(){return(
{top: 30, right: 60, bottom: 10, left: 60}
)});
  main.variable(observer("d3")).define("d3", ["require"], function(require){return(
require("d3@6")
)});
  return main;
}
