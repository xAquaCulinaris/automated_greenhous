<html>
<head>
<title>Measuring Data</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    
<style>
    
    html
    {
        background-color: rebeccapurple;
        font-family: sans-serif;
    }
    .btn 
    {
        background-color: DodgerBlue;
        border: none;
        color: white;
        padding: 12px 30px;
        cursor: pointer;
        font-size: 20px;
        
    }
    
    .div{
        width: 20%;
        margin: 0 auto;
        
    }
    .text {
        position: relative;
        float: left;
    }
    .data {
        position: relative;
        float: right;
    }
    #download_form{
        position: relative;
        margin: 0 auto;
        width: 20%;
        text-align: center;
    }
    

    /* Darker background on mouse-over */
    .btn:hover 
    {
      background-color: RoyalBlue;
    }
    
    h1{text-align: center;}
    
</style>

    
</head>
<body>

    <h1>Measuring</h1>
    
    <div class="div">
        
    <div class="text">
        <p>Terperature Inside:</p>
        <p>Terperature Outside:</p>
        <p>Plant[1] ground:</p>
        <p>Plant[2] ground:</p>
        <p>Water level:</p>
	<p>Light level:</p>

    </div>
        
    <!-- Messwerte aus XML auslesen und anzeigen -->
    <div class="data">
        <?php
        $xmlFile = 'data.xml';
        if (file_exists($xmlFile)) { 
        $xml = simplexml_load_file($xmlFile); 
        $data = $xml->data[0];
        echo '<p>'.$data->tempInside.'</p>';
        echo'<p>'.$data->tempOutside.'</p>';
        echo'<p>'.$data->plant1.'</p>';
        echo'<p>'.$data->plant2.'</p>';
        echo'<p>'.$data->waterLevel.'</p>';
	echo'<p>'.$data->light.'</p>';

        }
        ?>
    </div>
        
    </div>
    
    <form action="logfile.log" method="get" target="_blank" id="download_form">    
    <center><button class="btn"><i class="fa fa-download"></i> Download</button></center>
    </form>


</body>
</html>