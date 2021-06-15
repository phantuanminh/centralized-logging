import React, { useState } from "react";
import Avatar from "@material-ui/core/Avatar";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import LockOutlinedIcon from "@material-ui/icons/LockOutlined";
import Typography from "@material-ui/core/Typography";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
  paper: {
    margin: theme.spacing(6, 4),
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main,
  },
  form: {
    width: "100%", // Fix IE 11 issue.
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
}));

const MessageForm = () => {
  const classes = useStyles();
  const [topic, setTopic] = useState("");
  const [partition, setPartition] = useState(0);
  const [message, setMessage] = useState("");

  return (
    <div className={classes.paper}>
      <Avatar className={classes.avatar}>
        <LockOutlinedIcon />
      </Avatar>
      <Typography component="h1" variant="h5">
        Kafka Client
      </Typography>
      <form className={classes.form} noValidate>
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          id="email"
          label="Topic"
          name="email"
          autoComplete="topic"
          autoFocus
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        />
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          name="partition"
          label="Partition"
          type="number"
          id="partition"
          InputLabelProps={{
            shrink: true,
          }}
          autoComplete="partition"
          value={partition}
          onChange={(e) => setPartition(e.target.value)}
        />
        <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          name="message"
          label="Message"
          type="text"
          id="message"
          autoComplete="message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <Button
          fullWidth
          variant="contained"
          color="primary"
          className={classes.submit}
          onClick={async () => {
            const data = { topic, partition, message };
            const response = await fetch("/api/message", {
              crossDomain: true,
              method: "POST",
              mode: "cors",
              cache: "no-cache",
              credentials: "same-origin",
              headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS, GET, POST",
              },
              body: JSON.stringify(data),
            });

            if (response.ok) {
              console.log("respond work");
              const data = await response.json();
              console.log(data);
            }
          }}
        >
          Publish
        </Button>
      </form>
    </div>
  );
};

export default MessageForm;
