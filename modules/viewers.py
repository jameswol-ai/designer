import math
import plotly.graph_objects as go
import streamlit as st

from engine.viewers import VIEW_MODES, model_summary
from engine.layout import generate_layout
from engine.furniture import furniture_schedule
from engine.structure_grid import candidate_grids
from engine.vertical import stair_schedule
from engine.environment import environmental_checks
from engine.egress import egress_summary
from engine.site import parking_plan


def _floor_plan(project, floor=1, labels=True, grid=True):
    layout = generate_layout(project)
    fig = go.Figure()
    for r in layout:
        if r.get("floor", 1) != floor:
            continue
        fig.add_shape(type="rect", x0=r["x"], y0=r["y"], x1=r["x"]+r["width"], y1=r["y"]+r["depth"], line=dict(width=2))
        if labels:
            fig.add_annotation(x=r["x"]+r["width"]/2, y=r["y"]+r["depth"]/2, text=f"{r['name']}<br>{r['area']:.1f} m²", showarrow=False)
    if grid:
        for v in range(0, 40, 5):
            fig.add_vline(x=v, line_width=1, opacity=0.2)
            fig.add_hline(y=v, line_width=1, opacity=0.2)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=620, xaxis_title="m", yaxis_title="m", margin=dict(l=20,r=20,t=20,b=20))
    return fig


def _stacked_model(project):
    s = model_summary(project); fig = go.Figure()
    for floor in range(project.floors):
        z=floor*3.2
        fig.add_trace(go.Mesh3d(x=[0,s["floor_width_m"],s["floor_width_m"],0], y=[0,0,s["floor_depth_m"],s["floor_depth_m"]], z=[z,z,z,z], i=[0,0],j=[1,2],k=[2,3],opacity=0.55,name=f"Floor {floor+1}"))
    fig.update_layout(height=650,scene=dict(xaxis_title="X (m)",yaxis_title="Y (m)",zaxis_title="Z (m)"),margin=dict(l=0,r=0,t=20,b=0)); return fig


def _elevation(project, title, depth=False):
    s=model_summary(project); span=s["floor_depth_m"] if depth else s["floor_width_m"]; height=project.floors*3.2; fig=go.Figure()
    fig.add_shape(type="rect",x0=0,y0=0,x1=span,y1=height,line=dict(width=2))
    for floor in range(1,project.floors): fig.add_shape(type="line",x0=0,y0=floor*3.2,x1=span,y1=floor*3.2,line=dict(width=1))
    fig.add_annotation(x=span/2,y=height+0.5,text=title,showarrow=False); fig.update_yaxes(scaleanchor="x",scaleratio=1); fig.update_layout(height=550,xaxis_title="m",yaxis_title="Height (m)"); return fig


def render(project):
    st.subheader("Architectural Viewers")
    st.caption("Conceptual visualization of the current architectural model. Preliminary geometry only.")
    view=st.selectbox("View",VIEW_MODES,index=min(2,len(VIEW_MODES)-1))
    if view=="Dashboard": st.info("Use the Dashboard workspace for project metrics and scoring.")
    elif view=="3D Model": st.plotly_chart(_stacked_model(project),use_container_width=True)
    elif view=="Floor Plan":
        floor=st.slider("Floor",1,max(1,project.floors),1); a,b=st.columns(2); labels=a.checkbox("Room labels",True); grid=b.checkbox("Grid overlay",True); st.plotly_chart(_floor_plan(project,floor,labels,grid),use_container_width=True)
    elif view=="Site Plan":
        st.plotly_chart(_floor_plan(project),use_container_width=True); st.dataframe([parking_plan(project)],use_container_width=True,hide_index=True)
    elif view=="Elevations": st.plotly_chart(_elevation(project,"Elevation"),use_container_width=True)
    elif view=="Sections": st.plotly_chart(_elevation(project,"Section",True),use_container_width=True)
    else:
        st.write("Furniture and equipment"); st.dataframe(furniture_schedule(project),use_container_width=True,hide_index=True)
        st.write("Structural grid candidates"); st.dataframe(candidate_grids(project),use_container_width=True,hide_index=True)
        st.write("Vertical circulation"); st.dataframe(stair_schedule(project),use_container_width=True,hide_index=True)
        st.write("Environmental analysis"); st.dataframe(environmental_checks(project),use_container_width=True,hide_index=True)
        st.write("Egress summary"); st.json(egress_summary(project))
