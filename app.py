import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NEON MAZE — Cyber Chase",
    page_icon="🟣",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .block-container {padding-top: 1.2rem; padding-bottom: 0.5rem; max-width: 1000px;}
    [data-testid="stHeader"] {background: transparent;}
    .title {
        text-align:center;
        font-size:2.3rem;
        font-weight:800;
        letter-spacing:3px;
        margin-bottom:0;
    }
    .subtitle {
        text-align:center;
        opacity:.75;
        margin-top:.1rem;
        margin-bottom:.8rem;
    }
</style>
<div class="title">⚡ NEON MAZE</div>
<div class="subtitle">CYBER CHASE • Collect energy • Outsmart the drones • Reach the portal</div>
""", unsafe_allow_html=True)

GAME_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
*{box-sizing:border-box}
body{
    margin:0;
    background:#070914;
    color:#eef2ff;
    font-family:Arial,Helvetica,sans-serif;
    overflow:hidden;
}
.wrap{
    width:100%;
    max-width:900px;
    margin:auto;
    display:flex;
    flex-direction:column;
    align-items:center;
}
.hud{
    width:100%;
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:8px;
    margin-bottom:8px;
}
.card{
    background:#10162a;
    border:1px solid #26345e;
    border-radius:10px;
    padding:7px 5px;
    text-align:center;
    font-size:12px;
}
.card b{
    display:block;
    font-size:18px;
    margin-top:2px;
}
canvas{
    display:block;
    width:min(100%, 700px);
    height:auto;
    border-radius:14px;
    border:2px solid #283d77;
    background:#050711;
    box-shadow:0 0 25px rgba(80,110,255,.18);
    outline:none;
}
.help{
    margin-top:7px;
    text-align:center;
    font-size:12px;
    opacity:.72;
}
button{
    border:0;
    border-radius:9px;
    background:#202b50;
    color:white;
    padding:8px 14px;
    font-weight:700;
    cursor:pointer;
}
button:hover{background:#304275}
.overlay{
    position:absolute;
    inset:0;
    display:flex;
    align-items:center;
    justify-content:center;
    background:rgba(3,5,15,.78);
    border-radius:14px;
}
.panel{
    width:78%;
    max-width:430px;
    text-align:center;
    padding:25px;
    border:1px solid #405ca8;
    border-radius:16px;
    background:#0c1122;
    box-shadow:0 0 35px rgba(71,105,255,.2);
}
.panel h1{margin:0 0 8px;font-size:30px}
.panel p{opacity:.78;line-height:1.5}
#gamebox{position:relative;width:min(100%,700px)}
</style>
</head>
<body>
<div class="wrap">
    <div class="hud">
        <div class="card">SCORE<b id="score">0</b></div>
        <div class="card">LIVES<b id="lives">❤❤❤</b></div>
        <div class="card">SECTOR<b id="level">1 / 5</b></div>
        <div class="card">ENERGY<b id="energy">0%</b></div>
    </div>

    <div id="gamebox">
        <canvas id="game" width="672" height="600" tabindex="0"></canvas>
        <div class="overlay" id="overlay">
            <div class="panel">
                <h1 id="ovTitle">NEON MAZE</h1>
                <p id="ovText">
                    You are a data runner trapped inside a shifting cyber maze.
                    Collect enough energy cells, then reach the portal.
                </p>
                <button id="startBtn">START MISSION</button>
            </div>
        </div>
    </div>

    <div class="help">
        Move with <b>WASD</b> or <b>← ↑ ↓ →</b> • Collect cyan energy • Avoid drones •
        <b>P</b> pause • <b>R</b> restart
    </div>
</div>

<script>
(() => {
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const overlay = document.getElementById("overlay");
const ovTitle = document.getElementById("ovTitle");
const ovText = document.getElementById("ovText");
const startBtn = document.getElementById("startBtn");

const COLS = 28, ROWS = 25, TILE = 24;
const W = canvas.width, H = canvas.height;

const layouts = [
[
"############################",
"#............##............#",
"#.####.#####.##.#####.####.#",
"#.#  #.#   #.##.#   #.#  #.#",
"#.#.##.#.#.#....#.#.#.##.#.#",
"#..........................#",
"#.####.##.########.##.####.#",
"#......##....##....##......#",
"######.#####.##.#####.######",
"     #.#....      ....#.#   ",
"######.#.###.####.###.#.####",
"#............##............#",
"#.####.#####.##.#####.####.#",
"#.#  #.#   #....#   #.#  #.#",
"#.#.##.#.#.##..##.#.#.##.#.#",
"#..........................#",
"#.####.##.########.##.####.#",
"#......##....##....##......#",
"######.#####.##.#####.######",
"#............##............#",
"#.####.#####.##.#####.####.#",
"#.#......................#.#",
"#.########################.#",
"#............E.............#",
"############################"
],
[
"############################",
"#......#........#..........#",
"#.####.#.######.#.#######..#",
"#......#....#...#.....#....#",
"###.#########.#########.####",
"#...#................#.....#",
"#.#.#.##############.#.###.#",
"#.#.#........#.......#...#.#",
"#.#.########.#.#########.#.#",
"#.#..........#...........#.#",
"#.############.###########.#",
"#............E.............#",
"#.############.###########.#",
"#.#..........#...........#.#",
"#.#.########.#.#########.#.#",
"#.#.#........#.......#...#.#",
"#.#.#.##############.#.###.#",
"#...#................#.....#",
"###.#########.#########.####",
"#......#....#...#.....#....#",
"#.####.#.######.#.#######..#",
"#......#........#..........#",
"#.########################.#",
"#..........................#",
"############################"
],
[
"############################",
"#....#.......#.......#.....#",
"#.##.#.#####.#.#####.#.##..#",
"#....#.#...#.#.#...#.#....#",
"####.#.#.#.#.#.#.#.#.#.####",
"#....#...#.#...#.#...#....#",
"#.########.#####.########.#",
"#.#......................#.#",
"#.#.####################.#.#",
"#.#.#..................#.#.#",
"#.#.#.################.#.#.#",
"#.#.#......E...........#.#.#",
"#.#.####################.#.#",
"#.#......................#.#",
"#.########################.#",
"#..........................#",
"#.########################.#",
"#.#......................#.#",
"#.#.####################.#.#",
"#.#......................#.#",
"#.########################.#",
"#..........................#",
"#.########################.#",
"#..........................#",
"############################"
],
[
"############################",
"#........#........#........#",
"#.######.#.######.#.######.#",
"#.#....#.#.#....#.#.#....#.#",
"#.#.##.#.#.#.##.#.#.#.##.#.#",
"#...##...#...##...#...##...#",
"###.#######.#######.####.###",
"#..........................#",
"#.########################.#",
"#...........#..............#",
"#.#########.#.############.#",
"#...........E..............#",
"#.#########.#.############.#",
"#...........#..............#",
"#.########################.#",
"#..........................#",
"###.#######.#######.####.###",
"#...##...#...##...#...##...#",
"#.#.##.#.#.#.##.#.#.#.##.#.#",
"#.#....#.#.#....#.#.#....#.#",
"#.######.#.######.#.######.#",
"#........#........#........#",
"#.########################.#",
"#..........................#",
"############################"
],
[
"############################",
"#..#......#......#......#..#",
"#.##.####.#.####.#.####.##.#",
"#....#....#....#.#....#....#",
"####.#.#########.#.#########",
"#....#.....#.........#.....#",
"#.########.#.#######.#.###.#",
"#.#........#...#.....#...#.#",
"#.#.#############.#######.#.#",
"#.#.........#.............#.#",
"#.#########.#.############.#",
"#...........E..............#",
"#.#########.#.############.#",
"#.#.........#.............#.#",
"#.#.#############.#######.#.#",
"#.#........#...#.....#...#.#",
"#.########.#.#######.#.###.#",
"#....#.....#.........#.....#",
"####.#.#########.#.#########",
"#....#....#....#.#....#....#",
"#.##.####.#.####.#.####.##.#",
"#..#......#......#......#..#",
"#.########################.#",
"#..........................#",
"############################"
]
];

// Fix accidental spaces in layouts by treating spaces as open cells.
// All levels are intentionally different from the classic Pac-Man maze.

let grid, pellets, player, drones, portal;
let score = 0, lives = 3, level = 1, energy = 0;
let running = false, paused = false, last = 0, keys = {};
let requiredEnergy = 0, collected = 0;

const dirs = {
  up:{x:0,y:-1}, down:{x:0,y:1}, left:{x:-1,y:0}, right:{x:1,y:0}
};
const keyMap = {
  ArrowUp:"up", ArrowDown:"down", ArrowLeft:"left", ArrowRight:"right",
  w:"up",W:"up",s:"down",S:"down",a:"left",A:"left",d:"right",D:"right"
};

function normalizeLayout(raw){
    let out = raw.map(row => row.padEnd(COLS,"#").slice(0,COLS).split(""));
    // Remove spaces: they become corridors.
    for(let y=0;y<ROWS;y++) for(let x=0;x<COLS;x++){
        if(out[y][x] === " ") out[y][x] = ".";
    }
    return out;
}

function openCell(x,y){
    if(x<0 || y<0 || x>=COLS || y>=ROWS) return false;
    return grid[y][x] !== "#";
}

function center(x,y){ return {x:x*TILE+TILE/2,y:y*TILE+TILE/2}; }

function makePellets(){
    pellets=[];
    for(let y=0;y<ROWS;y++){
        for(let x=0;x<COLS;x++){
            if(grid[y][x]==="."){
                // Leave the starting area and portal area less crowded.
                if(!(x>=12&&x<=15&&y>=20&&y<=23))
                    pellets.push({x,y,active:true});
            }
        }
    }
    // Add a few special energy cells.
    for(let i=0;i<pellets.length;i+=Math.max(8,Math.floor(17-level))){
        pellets[i].special=true;
    }
    requiredEnergy = Math.max(6, Math.ceil(pellets.length*0.45));
    collected=0;
}

function makeDrones(){
    const starts = [
      {x:13,y:11},{x:14,y:11},{x:15,y:11},{x:14,y:13}
    ];
    drones = starts.slice(0, Math.min(4, 2 + Math.floor((level+1)/2))).map((p,i)=>({
        x:p.x*TILE+TILE/2, y:p.y*TILE+TILE/2,
        dir:["left","right","up","down"][i%4],
        speed: 1.15 + level*0.16 + i*0.04,
        phase:i*20
    }));
}

function newLevel(resetScore=false){
    if(resetScore) score=0;
    grid=normalizeLayout(layouts[level-1]);
    makePellets();

    // Find safe player spawn.
    let p={x:1,y:ROWS-2};
    for(let y=ROWS-2;y>=1;y--){
      for(let x=1;x<10;x++){
        if(openCell(x,y)){p={x,y};break;}
      }
      if(openCell(p.x,p.y)) break;
    }
    player={
      x:p.x*TILE+TILE/2,y:p.y*TILE+TILE/2,
      dir:"right", next:"right", speed:2.65 + level*0.08,
      invuln:0, trail:[]
    };

    // Portal location is the E tile, otherwise a fixed safe corridor.
    let found=false;
    for(let y=0;y<ROWS;y++) for(let x=0;x<COLS;x++){
      if(grid[y][x]==="E"){portal={x,y};grid[y][x]=".";found=true;}
    }
    if(!found) portal={x:COLS-2,y:1};
    makeDrones();
    updateHUD();
}

function resetMission(){
    score=0;lives=3;level=1;paused=false;
    newLevel();
    showOverlay("NEON MAZE","Collect at least 45% of the energy cells, then enter the portal. Drones get faster in every sector.","START MISSION");
}

function showOverlay(title,text,button){
    ovTitle.textContent=title;
    ovText.textContent=text;
    startBtn.textContent=button;
    overlay.style.display="flex";
}

function hideOverlay(){ overlay.style.display="none"; }

function start(){
    if(level>5){resetMission();return;}
    running=true;paused=false;hideOverlay();canvas.focus();
    last=performance.now();
    requestAnimationFrame(loop);
}

startBtn.addEventListener("click",start);

window.addEventListener("keydown",e=>{
    if(keyMap[e.key]){ keys[keyMap[e.key]]=true; e.preventDefault(); }
    if(e.key==="p"||e.key==="P"){
        if(running && overlay.style.display==="none"){
            paused=!paused;
            if(paused) showOverlay("PAUSED","Press P to return to the mission.","RESUME");
            else hideOverlay();
        }
    }
    if(e.key==="r"||e.key==="R"){
        resetMission();
    }
    if(e.key==="Enter" && overlay.style.display!=="none") start();
});
window.addEventListener("keyup",e=>{
    if(keyMap[e.key]) keys[keyMap[e.key]]=false;
});

function nearWall(nx,ny,r=7){
    const pts=[
      [nx-r,ny-r],[nx+r,ny-r],[nx-r,ny+r],[nx+r,ny+r]
    ];
    for(const [px,py] of pts){
      const tx=Math.floor(px/TILE),ty=Math.floor(py/TILE);
      if(!openCell(tx,ty)) return true;
    }
    return false;
}

function movePlayer(){
    if(player.invuln>0) player.invuln--;

    for(const name of Object.keys(keys)){
        if(keys[name]) player.next=name;
    }
    const nd=dirs[player.next];
    if(nd && !nearWall(player.x+nd.x*player.speed,player.y+nd.y*player.speed)){
        player.dir=player.next;
    }
    const d=dirs[player.dir];
    if(d && !nearWall(player.x+d.x*player.speed,player.y+d.y*player.speed)){
        player.x+=d.x*player.speed;
        player.y+=d.y*player.speed;
    }

    // Tunnel-like wrap at left/right corridors.
    if(player.x<-5) player.x=W+5;
    if(player.x>W+5) player.x=-5;

    const gx=Math.floor(player.x/TILE), gy=Math.floor(player.y/TILE);
    for(const p of pellets){
        if(!p.active) continue;
        if(p.x===gx && p.y===gy){
            p.active=false;
            collected++;
            score += p.special ? 40 : 10;
            if(p.special) score += 20;
            updateHUD();
        }
    }
    player.trail.push({x:player.x,y:player.y,a:1});
    if(player.trail.length>14) player.trail.shift();
}

function validDroneDirections(d){
    const arr=[];
    for(const [name,v] of Object.entries(dirs)){
        if(name===opposite(d)) continue;
        if(!nearWall(d.x+v.x*8,d.y+v.y*8,6)) arr.push(name);
    }
    return arr;
}
function opposite(d){
    return d==="up"?"down":d==="down"?"up":d==="left"?"right":"left";
}

function updateDrones(){
    for(const d of drones){
        const options=validDroneDirections(d);
        const px=player.x, py=player.y;
        const dist=Math.hypot(px-d.x,py-d.y);

        // Smart chase: periodically choose the direction that reduces distance.
        if(options.length && (Math.random()<0.055+level*0.008 || dist<130)){
            let best=options[0], bestScore=Infinity;
            for(const name of options){
                const v=dirs[name];
                const nx=d.x+v.x*18, ny=d.y+v.y*18;
                const s=Math.hypot(px-nx,py-ny)+(Math.random()*75);
                if(s<bestScore){bestScore=s;best=s?name:name;}
            }
            d.dir=best;
        }

        const v=dirs[d.dir];
        if(v && !nearWall(d.x+v.x*d.speed,d.y+v.y*d.speed,6)){
            d.x+=v.x*d.speed;d.y+=v.y*d.speed;
        }else if(options.length){
            d.dir=options[Math.floor(Math.random()*options.length)];
        }

        if(d.x<-5)d.x=W+5;if(d.x>W+5)d.x=-5;

        if(player.invuln<=0 && Math.hypot(player.x-d.x,player.y-d.y)<13){
            loseLife();
        }
    }
}

function loseLife(){
    player.invuln=150;
    lives--;
    updateHUD();
    if(lives<=0){
        running=false;
        showOverlay("MISSION FAILED","The drones caught you. Your final score was "+score+".","TRY AGAIN");
        return;
    }
    // Respawn without resetting collected energy.
    player.x=2*TILE+TILE/2;
    player.y=(ROWS-2)*TILE+TILE/2;
    player.dir="right";player.next="right";
}

function portalReady(){
    return collected>=requiredEnergy;
}

function checkPortal(){
    if(portalReady()){
        const px=portal.x*TILE+TILE/2, py=portal.y*TILE+TILE/2;
        if(Math.hypot(player.x-px,player.y-py)<15){
            score += 250*level;
            if(level===5){
                running=false;
                level=6;
                updateHUD();
                showOverlay("SYSTEM ESCAPED","You cleared all five sectors. Final score: "+score+" — excellent navigation!","PLAY AGAIN");
            }else{
                level++;
                score += 300;
                newLevel();
                showOverlay("SECTOR CLEARED","Portal reached! Sector "+level+" is more dangerous.","NEXT SECTOR");
            }
        }
    }
}

function updateHUD(){
    document.getElementById("score").textContent=score;
    document.getElementById("lives").textContent="❤".repeat(Math.max(0,lives))+"♡".repeat(Math.max(0,3-lives));
    document.getElementById("level").textContent=(level>5?5:level)+" / 5";
    const pct=Math.min(100,Math.round(collected/Math.max(1,requiredEnergy)*100));
    document.getElementById("energy").textContent=pct+"%";
}

function draw(){
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle="#050711";ctx.fillRect(0,0,W,H);

    // Subtle grid background.
    ctx.strokeStyle="rgba(70,95,170,.08)";
    ctx.lineWidth=1;
    for(let x=0;x<=W;x+=TILE){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
    for(let y=0;y<=H;y+=TILE){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}

    // Walls
    for(let y=0;y<ROWS;y++) for(let x=0;x<COLS;x++){
        if(grid[y][x]==="#"){
            const px=x*TILE,py=y*TILE;
            ctx.fillStyle="#111a38";
            ctx.fillRect(px+1,py+1,TILE-2,TILE-2);
            ctx.strokeStyle="#344fa0";
            ctx.strokeRect(px+3,py+3,TILE-6,TILE-6);
        }
    }

    // Energy cells
    for(const p of pellets){
        if(!p.active)continue;
        const px=p.x*TILE+TILE/2,py=p.y*TILE+TILE/2;
        ctx.beginPath();
        ctx.arc(px,py,p.special?5:2.5,0,Math.PI*2);
        ctx.fillStyle=p.special?"#3df6ff":"#9bc7ff";
        ctx.shadowBlur=p.special?14:5;ctx.shadowColor=ctx.fillStyle;
        ctx.fill();ctx.shadowBlur=0;
    }

    // Portal
    const pp=center(portal.x,portal.y);
    ctx.beginPath();
    ctx.arc(pp.x,pp.y,8+Math.sin(performance.now()/160)*2,0,Math.PI*2);
    ctx.strokeStyle=portalReady()?"#c95cff":"#39405d";
    ctx.lineWidth=3;ctx.shadowBlur=portalReady()?20:0;ctx.shadowColor="#c95cff";ctx.stroke();ctx.shadowBlur=0;
    ctx.fillStyle=portalReady()?"#c95cff":"#292d45";
    ctx.font="bold 9px Arial";ctx.textAlign="center";ctx.fillText("EXIT",pp.x,pp.y+3);

    // Player trail
    for(let i=0;i<player.trail.length;i++){
        const t=player.trail[i];
        ctx.globalAlpha=(i/player.trail.length)*.28;
        ctx.beginPath();ctx.arc(t.x,t.y,7,0,Math.PI*2);
        ctx.fillStyle="#7a5cff";ctx.fill();
    }
    ctx.globalAlpha=1;

    // Player orb
    ctx.beginPath();ctx.arc(player.x,player.y,8,0,Math.PI*2);
    ctx.fillStyle="#b9a5ff";ctx.shadowBlur=22;ctx.shadowColor="#7a5cff";ctx.fill();ctx.shadowBlur=0;
    ctx.beginPath();ctx.arc(player.x,player.y,3,0,Math.PI*2);
    ctx.fillStyle="#fff";ctx.fill();

    // Drones
    drones.forEach((d,i)=>{
        ctx.save();ctx.translate(d.x,d.y);
        ctx.rotate(performance.now()/700*(i%2?1:-1));
        ctx.fillStyle=["#ff4f8b","#ffb84d","#50e6ff","#9cff57"][i%4];
        ctx.shadowBlur=16;ctx.shadowColor=ctx.fillStyle;
        ctx.beginPath();
        ctx.moveTo(0,-9);ctx.lineTo(8,0);ctx.lineTo(0,9);ctx.lineTo(-8,0);ctx.closePath();ctx.fill();
        ctx.shadowBlur=0;
        ctx.fillStyle="#07101f";ctx.fillRect(-2,-2,4,4);
        ctx.restore();
    });

    // Objective text
    ctx.font="bold 12px Arial";
    ctx.fillStyle=portalReady()?"#c95cff":"#7e8bb5";
    ctx.textAlign="left";
    ctx.fillText(portalReady()?"PORTAL UNLOCKED — REACH EXIT":"COLLECT ENERGY TO UNLOCK PORTAL",10,H-9);
}

function loop(now){
    if(!running)return;
    if(!paused){
        const dt=Math.min(32,now-last); last=now;
        movePlayer();
        updateDrones();
        checkPortal();
        draw();
    }
    requestAnimationFrame(loop);
}

newLevel();
draw();
})();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=720, scrolling=False)

st.caption("🎮 Browser controls: WASD / Arrow Keys  •  P = Pause  •  R = Restart")
