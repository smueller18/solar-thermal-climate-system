/**
 * Created by Retter on 18.04.17.
 */

//Konstanten
const unit_radiation = "W/m"+"\u00B2";
const unit_power = "kW";
const unit_temperature = "°C";

function getElement(elementId) {
    return SVG.adopt(document.getElementById("k-building").contentDocument.getElementById(elementId));
}

window.onload = function() {
    var svg = getElement('Ebene_1');

    //Titel & Visualisation by
    var title = svg.text("Solare Klimatisierungsanlage - Fakultät W").font({size:30,family:'Verdana',weight:""}).move(290,10);

    svg.text("Visualisation by Christoph Retter - Hochschule Karlsruhe").font({
        family: 'Verdana',
        fill: '#aaaaaa',
        size: 8
        }).move(5, 529);

    //Ertragsanzeige

    var anzeige = svg.rect(190, 130).attr({fill: '#dddddd', stroke: '#000000'}).move(380, 210).stroke({
        width: 4,
        linejoin: 'round'
    });

    var img_location = window.location.origin + '/monitor/infographics/img/';

    var lab_solar_power = text(svg, "aktueller Solarertrag", anzeige.x() + 22, anzeige.y() + 17, true);
    var val_solar_power = text(svg,"0.0 " + unit_power ,lab_solar_power.x()+55,lab_solar_power.y()+23,false);

    var icon_solar_power = svg.image(img_location + 'solar-energy.svg', 24, 24).move(lab_solar_power.x() + 10, lab_solar_power.y() + 20);

    var lab_heat_power = text(svg, "aktuelle Heizleistung", anzeige.x() + 22, anzeige.y() + 75, true);
    var val_heat_power = text(svg,"0.0 " + unit_power ,lab_heat_power.x()+55,lab_heat_power.y()+23,false);
    var icon_heat_power = svg.image(img_location + 'heating.svg', 23, 23).move(lab_heat_power.x() + 10, lab_heat_power.y() + 20).opacity(0);
    var icon_cool_power = svg.image(img_location + 'air-conditioner.svg',25,25).move(lab_heat_power.x()+10,lab_heat_power.y()+20).opacity(0);

    // Warmwassertank
    var w_x = 270;
    var w_y= 423;
    var w_h = 60;
    text(svg,"Warmwassertank",w_x-30,w_y+w_h+25,true);
    var w_fac = w_h / 3.5;
    var w_h_fac = 15;
    var w_x_fac = 55;

    var lab_TSH0 = setMeasurePoint(svg,w_x - w_x_fac, w_y - w_h_fac + w_fac);
    var lab_TSH2 = setMeasurePoint(svg,w_x - w_x_fac, w_y - w_h_fac + 2 * w_fac);
    var lab_TSH3 = setMeasurePoint(svg,w_x - w_x_fac, w_y - w_h_fac + 3 * w_fac);
    var lab_TSH1 = setMeasurePoint(svg,w_x - w_x_fac, w_y - w_h_fac + 4 * w_fac);

    //AKM
    var akm_x = 380;
    var akm_y = 490;
    text(svg,"Adsorptions-\nkältemaschine",akm_x,akm_y,true);

    //Kaltwassertank
    var k_x = 517;
    var k_y = 437;
    text(svg,"Kaltwassertank",k_x-27,k_y+52,true);
    var k_fac = 16;

    var lab_TSC1 = setMeasurePoint(svg,k_x+40, k_y-12  + k_fac,true);
    var lab_TSC0 = setMeasurePoint(svg,k_x+40, k_y-12  + 2 * k_fac,true);

    //Strahlung
    var lab_total_radiation = text(svg, "Globalstrahlung", 40, 130, true);
    var val_total_radiation = text(svg, "0.0 " + unit_radiation, lab_total_radiation.x()+30, lab_total_radiation.y()+23, false);

    var lab_diffuse_radiation = text(svg, "diffuser Anteil", lab_total_radiation.x(), lab_total_radiation.y()+56, true);
    var val_diffuse_radiation = text(svg, "0.0 " + unit_radiation, lab_diffuse_radiation.x()+30, lab_diffuse_radiation.y()+23, false);

    //Kollektoren
    var flat_coll = getElement("Flat_Collector");
    var lab_flat_coll = text(svg,"Flachkollektoren",flat_coll.x()-15,flat_coll.y()-40,true);
    var val_flat_coll = text(svg,"0.0 " + unit_temperature,flat_coll.x()+70,flat_coll.y()-10,false);

    var tube_coll = getElement("Tube_Collector");
    var lab_tube_coll = text(svg,"Vakuumröhrenkollektoren",tube_coll.x()-45,tube_coll.y()-30,true);
    var val_tube_coll = text(svg,"0.0 " + unit_temperature,tube_coll.x()+100,tube_coll.y()-5,false);

    //Rückkühler
    var lab_recooler = text(svg,"Rückkühler",429,87,true);

    //Textliste enthält alle Elemente, die nachts gefärbt werden müssen
    var textArr = [title,lab_total_radiation,val_total_radiation,lab_diffuse_radiation,val_diffuse_radiation,lab_flat_coll,lab_tube_coll,val_flat_coll,val_tube_coll,lab_recooler];

    const cp_ty = 3.680; // Unit: kj/(kg*K)
    const density_ty = 1.033; // Unit: g/cm3
    const cp_wa=4.182;
    const density_wa=1;

    //Variablen für Bedingungen
    var clouds = true;
    var night = false;
    var val_night = 5; //Grenze zur Nacht
    var t1 = new Date();
    var t2 = new Date(t1.getTime()-65000);


    //Solarertrag
    var FVFS_SOP = 0;
    var TSOPO = 0;
    var TSOPI = 0;
    var PSOP = 0;
    var PSOS = 0;

    //Heiz-/Kühlleistung
    var FVFS_C_1 = 0;
    var TCO_1 = 0;
    var TCI_1 = 0;
    var PC_1 = 0;

    //Rückkühler
    var CCH_1 = false;
    var fan_on = false;

    var socket = io(SOCKET_URL);
    socket.on('connect', function () {

        console.log("Connected");


        socket.on('sensor_values', function (message) {

            if (typeof(message) === "undefined")
                return;

            if ('error' in message) {
                console.log(message.error);
                return;
            }

            if ('timestamp' in message && 'data' in message) {

                if (message.topic === "prod.stcs.roof.solar_radiation") {

                    val_diffuse_radiation.text(addUnit(message.data["diffuse_radiation"],unit_radiation));

                    var total_radiation = message.data["total_radiation"];
                    val_total_radiation.text(addUnit(total_radiation,unit_radiation));

                    t1 = new Date();
                    if(((t1.getTime() - t2.getTime()))>60000) {
                        if (total_radiation <= val_night && !night) {
                            nightOn(textArr);
                            night = true;
                            t2 = new Date();
                        }
                        else if (total_radiation > val_night && night) {
                            nightOff(textArr);
                            night = false;
                            t2 = new Date();
                        }
                    }

                    var sunshine_presence = message.data["sunshine_presence"];
                    if (!night) {
                        if (sunshine_presence && clouds){
                            cloudsOff();
                            clouds = false;
                        }
                        else if (!sunshine_presence && !clouds){
                            cloudsOn();
                            clouds = true;
                        }
                    }

                }

                else if (message.topic === "prod.stcs.chillii") {

                    //Warmwassertank
                    lab_TSH0.text(addUnit(message.data["TSH0"],unit_temperature));
                    lab_TSH1.text(addUnit(message.data["TSH1"],unit_temperature));
                    lab_TSH2.text(addUnit(message.data["TSH2"],unit_temperature));
                    lab_TSH3.text(addUnit(message.data["TSH3"],unit_temperature));

                    //Kaltwassertank
                    lab_TSC0.text(addUnit(message.data["TSC0"],unit_temperature));
                    lab_TSC1.text(addUnit(message.data["TSC1"],unit_temperature));

                    //Rückkühler
                    val_flat_coll.text(addUnit(message.data["TSOC_1"],unit_temperature));
                    val_tube_coll.text(addUnit(message.data["TSOC_2"],unit_temperature));

                    //Solarertrag
                    TSOPO = message.data["TSOPO"];
                    TSOPI = message.data["TSOPI"];
                    PSOP = message.data["PSOP"];
                    PSOS = message.data["PSOS"];

                    //Heizertrag
                    TCO_1 = message.data["TCO_1"];
                    TCI_1 = message.data["TCI_1"];
                    PC_1 = message.data["PC_1"];

                    //Recooler
                    CCH_1 = message.data["CCH_1"];
                    if (CCH_1 && !fan_on) {
                        fanOn();
                        fan_on = true;
                    }
                    else if (!CCH_1 && fan_on){
                        fanOff();
                        fan_on = false;
                    }

                }

                else if (message.topic === "prod.stcs.cellar.flows"){
                    FVFS_SOP = message.data["FVFS_SOP"]; //Solarertrag
                    FVFS_C_1 = message.data["FVFS_C_1"]; //Heizertrag
                }

                setValue(val_solar_power,FVFS_SOP,cp_ty,TSOPO,TSOPI,density_ty,PSOP,PSOS,lab_solar_power);
                setValue(val_heat_power,FVFS_C_1,cp_wa,TCO_1,TCI_1,density_wa,PC_1,0,lab_heat_power,icon_heat_power,icon_cool_power);
            }
        });
    });
};

function setMeasurePoint(svg,x,y,left=false){
    var val_t0 = text(svg, "37.8 °C", x, y, true);
    if (!left) svg.rect(10, 2).center(x+65, val_t0.cy());
    else svg.rect(10, 2).center(x-10, val_t0.cy());
    return val_t0;
}

function text (svg,str,x,y,label){
    var text = svg.text(str).move(x,y);
    if (label)text.font({family:'Verdana', size: 14, fill: '#000000',weight:""});
    else text.font({family:'Verdana', size: 16, fill: '#000000',weight:""});
    return text;
}

function setValue(label,flow,cp,T1,T2,density,condition1=1,condition2 = 0,text_label = null, heat_icon = null, cool_icon = null){
    if (condition1 === 0 && condition2 === 0){
        label.text(" - ");
        if (heat_icon) {
            text_label.text("Klimasystem inaktiv");
            heat_icon.opacity(0);
            cool_icon.opacity(1);
        }
        else {
            text_label.text("Solarsystem inaktiv");
        }
    }
    else {
        var val_power = calcPower(flow,cp,T1,T2,density);
        label.text(addUnit(Math.abs(val_power),unit_power,2));
        if (heat_icon){
            if (val_power < 0 ){
                text_label.text("aktuelle Heizleistung");
                heat_icon.opacity(1);
                cool_icon.opacity(0);
            }
            else {
                text_label.text("aktuelle Kühlleistung");
                heat_icon.opacity(0);
                cool_icon.opacity(1);
            }
        }
        else {
            text_label.text("aktueller Solarertrag");
        }
    }
}

function calcPower(flow,cp,T1,T2,density){
    return (flow*density/60*cp*(T1-T2));
}

function addUnit (val,unit,decimal=1){
    return val.toFixed(decimal).toString() + " " + unit;
}

function cloudsOn(delay=0){
    var clouds = getElement("Tageswolken");
    clouds.animate(3000, '<>',delay).opacity(1);
}

function cloudsOff(){
    getElement("Tageswolken").animate(3000).opacity(0);
}

function nightOn(textArr){
    var fac = 6;
    getElement("Himmel").animate(fac*1500,'<',500).opacity(0);
    getElement("Sonne").animate(fac*2000,'<>').move(-200,300).delay(200).move(-500,300);
    getElement("Tageslicht").animate(1,'<>',fac*2000).opacity(0);
    cloudsOff();
    for (var i=0;i<textArr.length;i++){
        textArr[i].animate(fac*1500,'<',500).font({fill:'#ffffff'});
    }

}

function nightOff(textArr){
    var fac = 6;
    getElement("Himmel").animate(fac*1500,'<',500).opacity(1);
    getElement("Sonne").move(-200,300).animate(fac*3000,'<>',500).move(0,3);
    getElement("Tageslicht").animate(1,'<>',fac*2000).opacity(1);
    cloudsOn(15500);
    for (var i=0;i<textArr.length;i++){
        textArr[i].animate(fac*1500,'<',500).font({fill:'#000000'});
    }
}

function fanOn(){
    var fans = ["Fan1", "Fan2", "Fan3"];
    fans.forEach(function(fan) {
        var fanObj = getElement(fan);
        x = fanObj.node.getBBox().x + fanObj.node.getBBox().width / 2
        y = fanObj.node.getBBox().y + fanObj.node.getBBox().height / 2
        fanObj.animate(1000).rotate(360, x-0.1, y+0.4).loop();
    });
}

function fanOff (){
    getElement("Fan1").stop();
    getElement("Fan2").stop();
    getElement("Fan3").stop();
}
